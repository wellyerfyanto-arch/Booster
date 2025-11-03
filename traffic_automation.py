from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import random
import time
import requests
import json
from fake_useragent import UserAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrafficAutomation:
    def __init__(self):
        self.ua = UserAgent()
        self.session_requests = requests.Session()
        
    def get_random_proxy(self):
        """Get random proxy from free proxy list"""
        try:
            # Using free proxy list - in production, use paid proxies for better reliability
            response = self.session_requests.get('https://proxylist.geonode.com/api/proxy-list?limit=50&page=1&sort_by=lastChecked&sort_type=desc')
            if response.status_code == 200:
                proxies = response.json().get('data', [])
                if proxies:
                    proxy = random.choice(proxies)
                    return f"http://{proxy['ip']}:{proxy['port']}"
        except:
            pass
        return None
    
    def check_ip_leak(self, driver):
        """Check for IP/DNS leaks"""
        try:
            # Test IP leak
            driver.get("https://httpbin.org/ip")
            time.sleep(2)
            ip_info = driver.find_element(By.TAG_NAME, "body").text
            logger.info(f"Current IP Info: {ip_info}")
            
            # Test DNS leak
            driver.get("https://dnsleaktest.com")
            time.sleep(5)
            
            return True
        except Exception as e:
            logger.error(f"Leak check failed: {e}")
            return False
    
    def setup_driver(self):
        """Setup Chrome driver with proxy and user agent"""
        chrome_options = Options()
        
        # Headless configuration for Render
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Random user agent
        user_agent = self.ua.random
        chrome_options.add_argument(f'--user-agent={user_agent}')
        logger.info(f"Using User Agent: {user_agent}")
        
        # Proxy configuration
        proxy = self.get_random_proxy()
        if proxy:
            chrome_options.add_argument(f'--proxy-server={proxy}')
            logger.info(f"Using Proxy: {proxy}")
        
        # Additional options for better stealth
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            # Execute stealth script
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            logger.error(f"Driver setup failed: {e}")
            raise
    
    def random_scroll(self, driver, direction="down"):
        """Random scrolling behavior"""
        scroll_duration = random.uniform(3, 8)
        start_time = time.time()
        
        if direction == "down":
            scroll_amount = random.randint(300, 800)
        else:
            scroll_amount = random.randint(-800, -300)
        
        while time.time() - start_time < scroll_duration:
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.5, 1.5))
    
    def find_and_click_post(self, driver):
        """Find and click a random post"""
        try:
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Look for common post selectors
            post_selectors = [
                "a[href*='/p/']",  # Instagram style
                "a[href*='/post/']",  # Common blog style
                ".post", ".article", ".card",
                "h1 a", "h2 a", "h3 a",
                "[class*='post'] a",
                "[class*='article'] a"
            ]
            
            for selector in post_selectors:
                try:
                    posts = driver.find_elements(By.CSS_SELECTOR, selector)
                    if posts:
                        post = random.choice(posts)
                        post_url = post.get_attribute('href')
                        if post_url and 'http' in post_url:
                            logger.info(f"Clicking post: {post_url}")
                            driver.execute_script("arguments[0].click();", post)
                            return True
                except:
                    continue
            
            # Fallback: click any link that looks like a post
            all_links = driver.find_elements(By.TAG_NAME, "a")
            if all_links:
                link = random.choice(all_links)
                driver.execute_script("arguments[0].click();", link)
                return True
                
        except Exception as e:
            logger.error(f"Failed to find/click post: {e}")
        
        return False
    
    def run_automation(self, url, session_id):
        """Main automation loop"""
        driver = None
        try:
            logger.info(f"Starting automation for: {url}")
            
            # Setup driver with proxy and user agent
            driver = self.setup_driver()
            
            # Step 1: Check for data leaks
            logger.info("Checking for data leaks...")
            if not self.check_ip_leak(driver):
                logger.warning("Potential data leak detected")
                # Continue anyway for demo purposes
            
            # Step 2: Open target URL
            logger.info(f"Opening URL: {url}")
            driver.get(url)
            time.sleep(random.uniform(5, 10))
            
            max_iterations = 3  # Limit iterations for demo
            
            for iteration in range(max_iterations):
                logger.info(f"Starting iteration {iteration + 1}")
                
                # Step 3: Scroll down with random duration
                logger.info("Scrolling down...")
                self.random_scroll(driver, "down")
                time.sleep(random.uniform(2, 4))
                
                # Step 4: Scroll up with random duration
                logger.info("Scrolling up...")
                self.random_scroll(driver, "up")
                time.sleep(random.uniform(2, 4))
                
                # Step 5: Click random post
                logger.info("Looking for posts to click...")
                if self.find_and_click_post(driver):
                    time.sleep(random.uniform(5, 10))
                    
                    # Step 6: Scroll on post page
                    logger.info("Scrolling on post page...")
                    self.random_scroll(driver, "down")
                    time.sleep(random.uniform(2, 4))
                    
                    self.random_scroll(driver, "up")
                    time.sleep(random.uniform(2, 4))
                    
                    self.random_scroll(driver, "down")
                    time.sleep(random.uniform(2, 4))
                    
                    # Step 7: Go back to home
                    logger.info("Returning to home...")
                    driver.back()
                    time.sleep(random.uniform(5, 8))
                else:
                    logger.warning("No posts found to click")
                
                # Random delay between iterations
                if iteration < max_iterations - 1:
                    delay = random.uniform(10, 20)
                    logger.info(f"Waiting {delay:.1f} seconds before next iteration")
                    time.sleep(delay)
            
            logger.info("Automation completed successfully")
            
        except Exception as e:
            logger.error(f"Automation failed: {e}")
            raise
        finally:
            if driver:
                driver.quit()
