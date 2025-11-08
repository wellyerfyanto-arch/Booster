import threading
import time
import os
import random
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TrafficAutomation:
    def __init__(self, session_id):
        self.session_id = session_id
        self.log_file = f"logs/traffic_logs_{session_id}.txt"
        self.is_running = True
        self.profile_threads = []
        
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
        
        # Initialize log file
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write(f"Traffic Automation Session: {session_id}\n")
            f.write(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n")
    
    def run_automation(self, url, session_id, num_profiles=1, login_google=False, 
                      google_email="", google_password="", user_agent_type="desktop",
                      visit_duration=30, click_ads=False, proxy_type="none",
                      premium_proxy_service="", premium_proxy_username="", 
                      premium_proxy_password="", manual_proxies=[]):
        """
        Run traffic automation with multiple Chrome profiles and enhanced features
        """
        self._log(f"Starting automation with {num_profiles} profiles")
        self._log(f"Target URL: {url}")
        self._log(f"User Agent Type: {user_agent_type}")
        self._log(f"Visit Duration: {visit_duration} seconds")
        self._log(f"Click Ads: {click_ads}")
        self._log(f"Proxy Type: {proxy_type}")
        self._log(f"Google Login: {login_google}")
        
        # Implementation for multiple Chrome profiles
        self.profile_threads = []
        for i in range(num_profiles):
            if not self.is_running:
                self._log("Automation stopped by user")
                break
                
            # Assign proxy for this profile
            proxy = None
            if proxy_type == 'premium' and premium_proxy_service:
                proxy = self._get_premium_proxy(premium_proxy_service, premium_proxy_username, premium_proxy_password, i)
                self._log(f"Profile {i}: Using premium proxy from {premium_proxy_service}")
            elif proxy_type == 'manual' and manual_proxies:
                proxy = manual_proxies[i % len(manual_proxies)]
                self._log(f"Profile {i}: Using manual proxy: {proxy}")
            
            profile_thread = threading.Thread(
                target=self._run_single_profile,
                args=(url, session_id, i, login_google, google_email, 
                      google_password, user_agent_type, visit_duration, 
                      click_ads, proxy)
            )
            self.profile_threads.append(profile_thread)
            profile_thread.start()
            
            # Stagger profile starts to avoid detection
            delay = random.uniform(2, 5)
            time.sleep(delay)
        
        # Wait for all profiles to complete
        for thread in self.profile_threads:
            thread.join()
        
        self._log(f"Automation completed for all {num_profiles} profiles")
    
    def _get_premium_proxy(self, service, username, password, profile_index):
        """Generate premium proxy based on service"""
        if service == 'oxylabs':
            # Oxylabs residential proxy format
            return f"http://{username}:{password}@pr.oxylabs.io:7777"
        elif service == 'smartproxy':
            # Smartproxy format
            return f"http://{username}:{password}@gate.smartproxy.com:7000"
        elif service == 'brightdata':
            # Bright Data format
            return f"http://{username}:{password}@zproxy.lum-superproxy.io:22225"
        elif service == 'netnut':
            # NetNut format
            return f"http://{username}:{password}@proxy.netnut.io:10000"
        else:
            # Default format for other services
            return f"http://{username}:{password}@proxy-{service}.com:8080"
    
    def _run_single_profile(self, url, session_id, profile_index, login_google,
                           google_email, google_password, user_agent_type, 
                           visit_duration, click_ads, proxy):
        """
        Run automation for a single Chrome profile
        """
        profile_id = f"{session_id}_profile_{profile_index}"
        
        try:
            self._log(f"Profile {profile_index}: Starting automation")
            self._log(f"Profile {profile_index}: Proxy: {proxy if proxy else 'No proxy'}")
            self._log(f"Profile {profile_index}: User Agent: {user_agent_type}")
            self._log(f"Profile {profile_index}: Visit Duration: {visit_duration}s")
            
            # Create Chrome profile directory
            profile_dir = f"chrome_profiles/{profile_id}"
            os.makedirs(profile_dir, exist_ok=True)
            
            # Simulate browser automation (replace with actual Selenium/Playwright code)
            self._log(f"Profile {profile_index}: Initializing Chrome browser...")
            
            # Simulate browser startup time
            time.sleep(random.uniform(1, 3))
            
            if not self.is_running:
                self._log(f"Profile {profile_index}: Stopped before navigation")
                return
            
            # Google login simulation
            if login_google:
                self._log(f"Profile {profile_index}: Performing Google login...")
                # Simulate login process
                time.sleep(random.uniform(2, 5))
                self._log(f"Profile {profile_index}: Google login completed")
            
            # Navigate to URL
            self._log(f"Profile {profile_index}: Navigating to {url}")
            time.sleep(random.uniform(1, 3))
            
            # Simulate browsing behavior
            self._log(f"Profile {profile_index}: Page loaded, simulating user behavior...")
            
            # Random scrolling and interactions
            scroll_actions = random.randint(2, 5)
            for i in range(scroll_actions):
                if not self.is_running:
                    break
                time.sleep(random.uniform(1, 3))
                self._log(f"Profile {profile_index}: Scrolling {i+1}/{scroll_actions}")
            
            # Click ads if enabled
            if click_ads and self.is_running:
                self._log(f"Profile {profile_index}: Looking for Google ads to click...")
                time.sleep(random.uniform(1, 2))
                # Simulate ad click (50% chance)
                if random.random() > 0.5:
                    self._log(f"Profile {profile_index}: Clicked on Google ad")
                    # Simulate navigation to ad URL
                    time.sleep(random.uniform(2, 5))
                    # Simulate returning to original page
                    time.sleep(random.uniform(1, 2))
                else:
                    self._log(f"Profile {profile_index}: No relevant ads found")
            
            # Wait for remaining visit duration
            elapsed_time = scroll_actions * 2 + (5 if click_ads else 0)
            remaining_time = max(5, visit_duration - elapsed_time)
            
            self._log(f"Profile {profile_index}: Remaining on page for {remaining_time} seconds...")
            
            # Simulate remaining visit time with occasional activity
            start_wait = time.time()
            while time.time() - start_wait < remaining_time and self.is_running:
                time.sleep(random.uniform(5, 10))
                if random.random() > 0.7:  # 30% chance of additional activity
                    self._log(f"Profile {profile_index}: Simulating additional user interaction")
            
            if not self.is_running:
                self._log(f"Profile {profile_index}: Stopped during visit")
                return
            
            self._log(f"Profile {profile_index}: Visit completed successfully")
            
        except Exception as e:
            self._log(f"Profile {profile_index}: Error - {str(e)}")
            # Log the full exception for debugging
            import traceback
            self._log(f"Profile {profile_index}: Traceback: {traceback.format_exc()}")
    
    def stop_automation(self):
        """Stop the automation process"""
        self.is_running = False
        self._log("Automation stop requested")
    
    def _log(self, message):
        """Log message to file and print to console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        print(log_message, end="")
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_message)
        except Exception as e:
            print(f"Error writing to log file: {e}")
    
    def get_logs(self):
        """Read and return log content"""
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error reading logs: {str(e)}"