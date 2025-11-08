import threading
import time
import os
import random
from datetime import datetime
import logging
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

class TrafficAutomation:
    def __init__(self, session_id):
        self.session_id = session_id
        self.log_file = f"logs/traffic_logs_{session_id}.txt"
        self.is_running = True
        
        os.makedirs("logs", exist_ok=True)
        os.makedirs("chrome_profiles", exist_ok=True)
        
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write(f"Traffic Automation Session: {session_id}\n")
            f.write("=" * 50 + "\n")
    
    def run_automation(self, url, session_id, num_profiles=1, login_google=False, 
                      google_email="", google_password="", user_agent_type="desktop",
                      visit_duration=30, click_ads=False, proxy_type="none",
                      premium_proxy_service="", premium_proxy_username="", 
                      premium_proxy_password="", manual_proxies=[]):
        """
        Real browser automation dengan Playwright saja
        """
        self._log(f"Starting {num_profiles} profiles for: {url}")
        
        threads = []
        for i in range(num_profiles):
            if not self.is_running:
                break
                
            thread = threading.Thread(
                target=self._run_profile,
                args=(url, i, user_agent_type, visit_duration, click_ads)
            )
            threads.append(thread)
            thread.start()
            time.sleep(random.uniform(2, 5))
        
        for thread in threads:
            thread.join()
        
        self._log("All profiles completed")
    
    def _run_profile(self, url, profile_index, user_agent_type, visit_duration, click_ads):
        """Run single profile dengan Playwright"""
        try:
            self._log(f"Profile {profile_index}: Starting browser")
            
            with sync_playwright() as p:
                # Launch browser dengan options yang compatible
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu'
                    ]
                )
                
                # Setup context
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080} if user_agent_type == 'desktop' 
                            else {'width': 390, 'height': 844},
                    user_agent=self._get_user_agent(user_agent_type)
                )
                
                page = context.new_page()
                
                # Navigate to URL
                self._log(f"Profile {profile_index}: Going to {url}")
                page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Simulate user behavior
                self._simulate_behavior(page, profile_index, visit_duration)
                
                # Close browser
                browser.close()
                self._log(f"Profile {profile_index}: Completed")
                
        except Exception as e:
            self._log(f"Profile {profile_index}: Error - {str(e)}")
    
    def _simulate_behavior(self, page, profile_index, visit_duration):
        """Simulate realistic user behavior"""
        start_time = time.time()
        
        while time.time() - start_time < visit_duration and self.is_running:
            # Random actions
            actions = [
                ("scroll", "Scrolling down"),
                ("wait", "Reading content"),
                ("scroll", "Scrolling up"),
                ("wait", "Viewing images")
            ]
            
            action, message = random.choice(actions)
            self._log(f"Profile {profile_index}: {message}")
            
            if action == "scroll":
                scroll_amount = random.randint(200, 800)
                page.mouse.wheel(0, scroll_amount)
            
            time.sleep(random.uniform(2, 5))
    
    def _get_user_agent(self, user_agent_type):
        """Get user agent string"""
        if user_agent_type == 'mobile':
            return 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        else:
            return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    
    def stop_automation(self):
        self.is_running = False
        self._log("Automation stopped")
    
    def _log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f'[{timestamp}] {message}\n'
        print(log_message)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message)
    
    def get_logs(self):
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return "Logs not available"
