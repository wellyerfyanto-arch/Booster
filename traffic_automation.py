from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from proxy_manager import ProxyManager
import random
import time
import requests
import json
from fake_useragent import UserAgent
import logging
import logging.handlers
import os
from datetime import datetime

# Setup logging with rotation
logger = logging.getLogger(__name__)

class TrafficAutomation:
    def __init__(self, session_id):
        self.ua = UserAgent()
        self.proxy_manager = ProxyManager()
        self.session_id = session_id
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for this session"""
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        # Create session-specific log file
        log_file = f'logs/session_{self.session_id}.log'
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(session_id)s] - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
        
        # Store log file path for access later
        self.log_file = log_file
    
    def log_message(self, message: str, level: str = "info"):
        """Log message with session context"""
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(message, extra={'session_id': self.session_id})
    
    def check_ip_leak(self, driver) -> bool:
        """Check for IP/DNS leaks with proxy verification"""
        try:
            self.log_message("Checking for IP leaks...")
            
            # Test 1: Check current IP
            driver.get("https://httpbin.org/ip")
            time.sleep(2)
            ip_info = driver.find_element(By.TAG_NAME, "body").text
            self.log_message(f"Current IP Info: {ip_info}")
            
            # Test 2: Check DNS
            driver.get("https://www.whatismydns.com")
            time.sleep(3)
            
            # Test 3: Check WebRTC (basic)
            driver.get("https://browserleaks.com/webrtc")
            time.sleep(2)
            
            self.log_message("IP leak check completed")
            return True
            
        except Exception as e:
            self.log_message(f"IP leak check failed: {e}", "warning")
            return True  # Continue anyway
    
    def setup_driver(self, max_retries: int = 3):
        """Setup Chrome driver with proxy rotation"""
        for attempt in range(max_retries):
            try:
                chrome_options = Options()
                
                # Headless configuration
                chrome_options.add_argument('--headless=new')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--window-size=1920,1080')
                
                # Random user agent
                user_agent = self.ua.random
                chrome_options.add_argument(f'--user-agent={user_agent}')
                self.log_message(f"Using User Agent: {user_agent}")
                
                # Proxy configuration
                if attempt > 0:  # Try proxy on retry
                    proxy_config = self.proxy_manager.get_working_proxy()
                else:
                    proxy_config = None
                
                if proxy_config:
                    proxy_url = proxy_config['http'].replace('http://', '')
                    chrome_options.add_argument(f'--proxy-server={proxy_url}')
                    self.log_message(f"Using proxy: {proxy_url}")
                else:
                    self.log_message("Using direct connection (no proxy)")
                
                # Stealth options
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                
                # Performance options
                prefs = {
                    'profile.default_content_setting_values': {
                        'images': 2,  # Disable images
                        'javascript': 1,  # Enable JavaScript
                        'plugins': 2,  # Disable plugins
                    }
                }
                chrome_options.add_experimental_option('prefs', prefs)
                
                driver = webdriver.Chrome(options=chrome_options)
                
                # Stealth modifications
                stealth_scripts = [
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
                    "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})",
                    "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})",
                ]
                
                for script in stealth_scripts:
                    driver.execute_script(script)
                
                self.log_message("Driver setup completed successfully")
                return driver
                
            except Exception as e:
                self.log_message(f"Driver setup attempt {attempt + 1} failed: {e}", "error")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2)
    
    def random_scroll(self, driver, direction: str = "down"):
        """Random scrolling behavior"""
        scroll_duration = random.uniform(2, 5)
        start_time = time.time()
        
        if direction == "down":
            scroll_range = (200, 500)
        else:
            scroll_range = (-500, -200)
        
        scroll_count = 0
        self.log_message(f"Starting {direction} scroll for {scroll_duration:.1f}s")
        
        while time.time() - start_time < scroll_duration and scroll_count < 10:
            try:
                scroll_amount = random.randint(scroll_range[0], scroll_range[1])
                driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                sleep_time = random.uniform(0.3, 1.0)
                time.sleep(sleep_time)
                scroll_count += 1
            except Exception as e:
                self.log_message(f"Scroll interrupted: {e}", "warning")
                break
        
        self.log_message(f"Completed {scroll_count} scroll actions")
    
    def find_and_click_post(self, driver, url: str) -> bool:
        """Find and click a random post"""
        try:
            self.log_message("Searching for posts to click...")
            
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Blogspot-specific selectors
            post_selectors = [
                "a[href*='.html']",
                ".post-title a",
                ".entry-title a",
                "h3.post-title a", 
                "h2.post-title a",
                ".blog-posts article h2 a",
                ".post-outer h3 a",
                "a[href*='/search?updated-max']",
                "a[href*='/p/']",
                "article a",
                ".post a",
            ]
            
            all_posts = []
            
            for selector in post_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        try:
                            href = element.get_attribute('href')
                            text = element.text.strip()
                            if href and len(text) > 5:
                                # Ensure it's from same domain
                                if url.split('/')[2] in href:
                                    all_posts.append((element, href, text))
                        except:
                            continue
                except:
                    continue
            
            # Fallback: all links
            if not all_posts:
                try:
                    all_links = driver.find_elements(By.TAG_NAME, "a")
                    for link in all_links:
                        try:
                            href = link.get_attribute('href')
                            text = link.text.strip()
                            if href and text and len(text) > 10:
                                if url.split('/')[2] in href and '#' not in href:
                                    all_posts.append((link, href, text))
                        except:
                            continue
                except:
                    pass
            
            if all_posts:
                # Remove duplicates by URL
                unique_posts = {}
                for element, href, text in all_posts:
                    if href not in unique_posts:
                        unique_posts[href] = (element, text)
                
                selected_href = random.choice(list(unique_posts.keys()))
                element, text = unique_posts[selected_href]
                
                self.log_message(f"Selected post: '{text[:30]}...' - {selected_href}")
                
                # Scroll to element
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                time.sleep(1)
                
                # Click using JavaScript
                driver.execute_script("arguments[0].click();", element)
                self.log_message("Successfully clicked post")
                return True
            
            self.log_message("No suitable posts found", "warning")
            return False
                
        except Exception as e:
            self.log_message(f"Failed to find/click post: {e}", "error")
            return False
    
    def simulate_human_behavior(self, driver, location: str = "homepage"):
        """Simulate human-like behavior"""
        behaviors = []
        
        if location == "homepage":
            behaviors = [
                lambda: self.random_scroll(driver, "down"),
                lambda: time.sleep(random.uniform(1, 3)),
                lambda: self.random_scroll(driver, "up"), 
                lambda: time.sleep(random.uniform(1, 2)),
                lambda: self.random_scroll(driver, "down"),
            ]
        else:  # post page
            behaviors = [
                lambda: self.random_scroll(driver, "down"),
                lambda: time.sleep(random.uniform(2, 4)),
                lambda: self.random_scroll(driver, "up"),
                lambda: time.sleep(random.uniform(1, 2)),
                lambda: self.random_scroll(driver, "down"),
            ]
        
        selected_behaviors = random.sample(behaviors, random.randint(2, 3))
        self.log_message(f"Simulating {len(selected_behaviors)} human behaviors on {location}")
        
        for i, behavior in enumerate(selected_behaviors):
            behavior()
        
        time.sleep(random.uniform(2, 4))
    
    def run_automation(self, url: str, session_id: str):
        """Main automation loop"""
        driver = None
        try:
            self.log_message(f"🚀 Starting automation for: {url}")
            
            # Setup driver with proxy
            driver = self.setup_driver()
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            
            # Step 1: IP leak check
            self.log_message("Performing IP leak check...")
            self.check_ip_leak(driver)
            
            # Step 2: Open target URL
            self.log_message(f"Opening main URL: {url}")
            driver.get(url)
            time.sleep(random.uniform(5, 8))
            
            max_iterations = 2
            
            for iteration in range(max_iterations):
                self.log_message(f"🔄 Starting iteration {iteration + 1}/{max_iterations}")
                
                # Steps 3-4: Scroll behavior on homepage
                self.log_message("Simulating browsing behavior on homepage")
                self.simulate_human_behavior(driver, "homepage")
                
                # Step 5: Find and click post
                post_clicked = self.find_and_click_post(driver, url)
                
                if post_clicked:
                    self.log_message("✅ Successfully navigated to post")
                    time.sleep(random.uniform(4, 7))
                    
                    # Step 6: Simulate reading behavior on post
                    self.log_message("Simulating reading behavior on post")
                    self.simulate_human_behavior(driver, "post")
                    time.sleep(random.uniform(3, 5))
                    
                    # Step 7: Return to home (unless last iteration)
                    if iteration < max_iterations - 1:
                        self.log_message("Returning to homepage")
                        driver.back()
                        time.sleep(random.uniform(4, 6))
                else:
                    self.log_message("No post clicked, continuing with extended browsing")
                    self.simulate_human_behavior(driver, "homepage")
                
                # Break between iterations
                if iteration < max_iterations - 1:
                    wait_time = random.uniform(10, 15)
                    self.log_message(f"⏳ Waiting {wait_time:.1f}s before next iteration")
                    time.sleep(wait_time)
            
            self.log_message("🎉 Automation completed successfully!")
            
        except TimeoutException:
            self.log_message("Page load timeout occurred", "warning")
        except Exception as e:
            self.log_message(f"❌ Automation failed: {e}", "error")
            raise
        finally:
            if driver:
                try:
                    driver.quit()
                    self.log_message("Browser closed successfully")
                except Exception as e:
                    self.log_message(f"Error closing browser: {e}", "warning")
    
    def get_logs(self) -> str:
        """Get session logs"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return "No logs available"
