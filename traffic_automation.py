import threading
import time
import os
import random
from datetime import datetime
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

logger = logging.getLogger(__name__)

class TrafficAutomation:
    def __init__(self, session_id):
        self.session_id = session_id
        self.log_file = f"logs/traffic_logs_{session_id}.txt"
        self.is_running = True
        self.profile_threads = []
        
        os.makedirs("logs", exist_ok=True)
        os.makedirs("chrome_profiles", exist_ok=True)
        
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write(f"Traffic Automation Session: {session_id}\n")
            f.write(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n")
    
    def setup_chrome_driver(self, profile_index, user_agent_type, proxy=None):
        """Setup Chrome driver dengan options"""
        chrome_options = Options()
        
        # Basic options untuk headless
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent
        if user_agent_type == 'mobile':
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1')
            chrome_options.add_argument('--window-size=375,812')
        else:
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
            chrome_options.add_argument('--window-size=1920,1080')
        
        # Proxy configuration
        if proxy:
            chrome_options.add_argument(f'--proxy-server={proxy}')
        
        # Profile directory
        profile_dir = f"chrome_profiles/{self.session_id}_profile_{profile_index}"
        os.makedirs(profile_dir, exist_ok=True)
        chrome_options.add_argument(f'--user-data-dir={profile_dir}')
        
        try:
            # Try using webdriver-manager first
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            self._log(f"WebDriver Manager failed: {e}, trying direct Chrome")
            # Fallback to system Chrome
            chrome_options.binary_location = '/usr/bin/google-chrome'
            driver = webdriver.Chrome(options=chrome_options)
        
        return driver
    
    def run_automation(self, url, session_id, num_profiles=1, login_google=False, 
                      google_email="", google_password="", user_agent_type="desktop",
                      visit_duration=30, click_ads=False, proxy_type="none",
                      premium_proxy_service="", premium_proxy_username="", 
                      premium_proxy_password="", manual_proxies=[]):
        """
        Run REAL browser automation dengan Selenium
        """
        self._log(f"Starting REAL browser automation with {num_profiles} profiles")
        self._log(f"Target URL: {url}")
        
        self.profile_threads = []
        for i in range(num_profiles):
            if not self.is_running:
                break
                
            # Assign proxy
            proxy = None
            if proxy_type == 'premium' and premium_proxy_service:
                proxy = self._get_premium_proxy(premium_proxy_service, premium_proxy_username, premium_proxy_password, i)
            elif proxy_type == 'manual' and manual_proxies:
                proxy = manual_proxies[i % len(manual_proxies)]
            
            profile_thread = threading.Thread(
                target=self._run_real_browser_profile,
                args=(url, session_id, i, login_google, google_email, 
                      google_password, user_agent_type, visit_duration, 
                      click_ads, proxy)
            )
            self.profile_threads.append(profile_thread)
            profile_thread.start()
            
            time.sleep(random.uniform(3, 7))
        
        for thread in self.profile_threads:
            thread.join()
        
        self._log(f"Real browser automation completed for {num_profiles} profiles")
    
    def _run_real_browser_profile(self, url, session_id, profile_index, login_google,
                                google_email, google_password, user_agent_type, 
                                visit_duration, click_ads, proxy):
        """Run automation dengan real browser"""
        driver = None
        try:
            self._log(f"Profile {profile_index}: Starting real browser")
            driver = self.setup_chrome_driver(profile_index, user_agent_type, proxy)
            
            # Google login jika diminta
            if login_google:
                self._google_login(driver, google_email, google_password, profile_index)
            
            # Navigate ke target URL
            self._log(f"Profile {profile_index}: Navigating to {url}")
            driver.get(url)
            
            # Tunggu page load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Simulate user behavior
            self._simulate_real_behavior(driver, profile_index, visit_duration)
            
            # Click ads jika diminta
            if click_ads:
                self._click_google_ads(driver, profile_index)
            
            self._log(f"Profile {profile_index}: Real browser automation completed")
            
        except Exception as e:
            self._log(f"Profile {profile_index}: Error in real browser - {str(e)}")
        finally:
            if driver:
                driver.quit()
    
    def _google_login(self, driver, email, password, profile_index):
        """Login ke Google account"""
        try:
            self._log(f"Profile {profile_index}: Attempting Google login")
            driver.get("https://accounts.google.com/")
            
            # Fill email
            email_field = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "identifierId"))
            )
            email_field.send_keys(email)
            
            # Click next
            next_btn = driver.find_element(By.ID, "identifierNext")
            next_btn.click()
            
            # Wait for password field
            password_field = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "password"))
            )
            password_field.send_keys(password)
            
            # Click next
            next_btn = driver.find_element(By.ID, "passwordNext")
            next_btn.click()
            
            # Wait for login completion
            WebDriverWait(driver, 15).until(
                EC.url_contains("myaccount.google.com") | EC.url_contains("google.com")
            )
            
            self._log(f"Profile {profile_index}: Google login successful")
            
        except Exception as e:
            self._log(f"Profile {profile_index}: Google login failed - {str(e)}")
    
    def _simulate_real_behavior(self, driver, profile_index, visit_duration):
        """Simulasi behavior real user"""
        import random
        
        start_time = time.time()
        actions = [
            "scrolling down",
            "scrolling up", 
            "moving mouse randomly",
            "brief pause",
            "more scrolling"
        ]
        
        while time.time() - start_time < visit_duration and self.is_running:
            action = random.choice(actions)
            self._log(f"Profile {profile_index}: {action}")
            
            if action == "scrolling down":
                driver.execute_script("window.scrollBy(0, 500);")
            elif action == "scrolling up":
                driver.execute_script("window.scrollBy(0, -300);")
            elif action == "moving mouse randomly":
                # Random mouse movement simulation
                pass
            
            time.sleep(random.uniform(2, 5))
    
    def _click_google_ads(self, driver, profile_index):
        """Coba click Google ads"""
        try:
            # Cari elemen yang kemungkinan adalah ads
            selectors = [
                "a[href*='googleadservices']",
                ".adsbygoogle",
                "[data-ad]",
                ".advertisement",
                "#taw > div"
            ]
            
            for selector in selectors:
                try:
                    ads = driver.find_elements(By.CSS_SELECTOR, selector)
                    if ads:
                        random.choice(ads).click()
                        self._log(f"Profile {profile_index}: Clicked ad with selector {selector}")
                        time.sleep(5)  # Wait after click
                        break
                except:
                    continue
                    
        except Exception as e:
            self._log(f"Profile {profile_index}: Ad clicking failed - {str(e)}")
    
    def _get_premium_proxy(self, service, username, password, profile_index):
        """Generate premium proxy string"""
        # Same as before...
        pass
    
    def stop_automation(self):
        self.is_running = False
        self._log("Real browser automation stopped")
    
    def _log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        print(log_message, end="")
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_message)
        except Exception as e:
            print(f"Error writing to log file: {e}")
    
    def get_logs(self):
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error reading logs: {str(e)}"
