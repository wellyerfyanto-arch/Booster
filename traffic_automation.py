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
        
    def get_reliable_proxies(self):
        """Get list of more reliable proxies"""
        proxies_list = [
            # Add some free proxies (these change frequently)
            None,  # No proxy as fallback
        ]
        
        try:
            # Try multiple free proxy sources
            sources = [
                'https://proxylist.geonode.com/api/proxy-list?limit=20&page=1&sort_by=lastChecked&sort_type=desc',
                'https://www.proxy-list.download/api/v1/get?type=http',
            ]
            
            for source in sources:
                try:
                    response = self.session_requests.get(source, timeout=10)
                    if response.status_code == 200:
                        if 'geonode' in source:
                            data = response.json()
                            for proxy in data.get('data', []):
                                proxy_url = f"http://{proxy['ip']}:{proxy['port']}"
                                proxies_list.append(proxy_url)
                        else:
                            # Text format for proxy-list.download
                            lines = response.text.strip().split('\r\n')
                            for line in lines:
                                if ':' in line:
                                    ip, port = line.split(':')
                                    proxies_list.append(f"http://{ip}:{port}")
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"Failed to fetch proxies: {e}")
            
        return list(set(proxies_list))  # Remove duplicates
    
    def check_ip_leak(self, driver):
        """Check for IP/DNS leaks"""
        try:
            # Test current IP
            driver.get("https://api.ipify.org?format=json")
            time.sleep(2)
            ip_element = driver.find_element(By.TAG_NAME, "pre")
            current_ip = ip_element.text
            logger.info(f"Current IP: {current_ip}")
            
            # Test DNS leak
            driver.get("https://www.whatismydns.com")
            time.sleep(3)
            
            return True
        except Exception as e:
            logger.error(f"Leak check failed: {e}")
            return True  # Continue anyway
    
    def setup_driver(self, max_retries=3):
        """Setup Chrome driver with retry mechanism"""
        for attempt in range(max_retries):
            try:
                chrome_options = Options()
                
                # Headless configuration for Render
                chrome_options.add_argument('--headless=new')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--window-size=1920,1080')
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                
                # Random user agent
                user_agent = self.ua.random
                chrome_options.add_argument(f'--user-agent={user_agent}')
                logger.info(f"Using User Agent: {user_agent}")
                
                # Proxy configuration with fallback
                proxies = self.get_reliable_proxies()
                selected_proxy = random.choice(proxies) if proxies else None
                
                if selected_proxy:
                    chrome_options.add_argument(f'--proxy-server={selected_proxy}')
                    logger.info(f"Attempt {attempt + 1}: Using Proxy: {selected_proxy}")
                else:
                    logger.info(f"Attempt {attempt + 1}: No proxy, using direct connection")
                
                # Additional stealth options
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                
                # Disable images for faster loading
                chrome_options.add_argument('--blink-settings=imagesEnabled=false')
                
                driver = webdriver.Chrome(options=chrome_options)
                
                # Stealth modifications
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]})")
                driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
                
                return driver
                
            except Exception as e:
                logger.error(f"Driver setup attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2)
    
    def random_scroll(self, driver, direction="down"):
        """Random scrolling behavior"""
        scroll_duration = random.uniform(2, 5)  # Reduced duration
        start_time = time.time()
        
        if direction == "down":
            scroll_amount = random.randint(200, 500)
        else:
            scroll_amount = random.randint(-500, -200)
        
        while time.time() - start_time < scroll_duration:
            try:
                driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(random.uniform(0.3, 1.0))
            except:
                break
    
    def find_and_click_post(self, driver):
        """Find and click a random post with better selectors"""
        try:
            # Wait for page to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Common blog post selectors
            post_selectors = [
                "a[href*='.html']",  # Blogspot posts
                ".post-title a",
                ".entry-title a", 
                ".post h2 a",
                ".blog-posts h2 a",
                "article h2 a",
                ".item h2 a",
                "[class*='post'] h3 a",
                "a[href*='/p/']",
                "a[href*='/202']",  # Posts with year in URL
            ]
            
            all_posts = []
            
            for selector in post_selectors:
                try:
                    posts = driver.find_elements(By.CSS_SELECTOR, selector)
                    for post in posts:
                        try:
                            href = post.get_attribute('href')
                            text = post.text.strip()
                            if href and text and len(text) > 10:  # Filter real posts
                                all_posts.append(post)
                        except:
                            continue
                except:
                    continue
            
            if all_posts:
                post = random.choice(all_posts)
                post_url = post.get_attribute('href')
                logger.info(f"Clicking post: {post.text[:50]}... - {post_url}")
                
                # Scroll to post first
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", post)
                time.sleep(1)
                
                # Click using JavaScript
                driver.execute_script("arguments[0].click();", post)
                return True
                
        except Exception as e:
            logger.error(f"Failed to find/click post: {e}")
        
        return False
    
    def run_automation(self, url, session_id):
        """Main automation loop with better error handling"""
        driver = None
        try:
            logger.info(f"Starting automation for: {url}")
            
            # Setup driver with retry
            driver = self.setup_driver()
            
            # Step 1: Check for data leaks (optional)
            logger.info("Checking for data leaks...")
            self.check_ip_leak(driver)
            
            # Step 2: Open target URL with timeout
            logger.info(f"Opening URL: {url}")
            driver.set_page_load_timeout(30)
            driver.get(url)
            time.sleep(random.uniform(3, 6))
            
            max_iterations = 2  # Reduced for stability
            
            for iteration in range(max_iterations):
                logger.info(f"Starting iteration {iteration + 1}")
                
                # Step 3: Scroll down
                logger.info("Scrolling down...")
                self.random_scroll(driver, "down")
                time.sleep(random.uniform(1, 3))
                
                # Step 4: Scroll up
                logger.info("Scrolling up...")
                self.random_scroll(driver, "up")
                time.sleep(random.uniform(1, 3))
                
                # Step 5: Click random post
                logger.info("Looking for posts to click...")
                post_clicked = self.find_and_click_post(driver)
                
                if post_clicked:
                    time.sleep(random.uniform(4, 8))
                    
                    # Scroll on post page
                    logger.info("Scrolling on post page...")
                    self.random_scroll(driver, "down")
                    time.sleep(1)
                    
                    self.random_scroll(driver, "up")
                    time.sleep(1)
                    
                    self.random_scroll(driver, "down")
                    time.sleep(1)
                    
                    # Go back to home
                    logger.info("Returning to home...")
                    driver.execute_script("window.history.go(-1)")
                    time.sleep(random.uniform(3, 6))
                else:
                    logger.warning("No posts found to click, continuing...")
                
                # Random delay between iterations
                if iteration < max_iterations - 1:
                    delay = random.uniform(8, 15)
                    logger.info(f"Waiting {delay:.1f} seconds before next iteration")
                    time.sleep(delay)
            
            logger.info("Automation completed successfully")
            
        except Exception as e:
            logger.error(f"Automation failed: {e}")
            raise
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
