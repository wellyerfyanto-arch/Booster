import threading
import time
import os
import random
from datetime import datetime
import logging
from playwright.sync_api import sync_playwright
import requests

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
    
    def run_automation(self, url, session_id, num_profiles=1, login_google=False, 
                      google_email="", google_password="", user_agent_type="desktop",
                      visit_duration=30, click_ads=False, proxy_type="none",
                      premium_proxy_service="", premium_proxy_username="", 
                      premium_proxy_password="", manual_proxies=[]):
        """
        Run REAL browser automation dengan Playwright
        """
        self._log(f"🚀 Starting REAL browser automation with {num_profiles} profiles")
        self._log(f"🎯 Target URL: {url}")
        self._log(f"📱 User Agent: {user_agent_type}")
        self._log(f"⏱️ Visit Duration: {visit_duration}s")
        self._log(f"🔎 Click Ads: {click_ads}")
        self._log(f"🔌 Proxy: {proxy_type}")
        
        self.profile_threads = []
        for i in range(num_profiles):
            if not self.is_running:
                self._log("🛑 Automation stopped by user")
                break
                
            # Assign proxy
            proxy_config = None
            if proxy_type == 'premium' and premium_proxy_service:
                proxy_config = self._get_premium_proxy_config(premium_proxy_service, premium_proxy_username, premium_proxy_password)
                self._log(f"👤 Profile {i}: Using premium proxy from {premium_proxy_service}")
            elif proxy_type == 'manual' and manual_proxies:
                proxy_config = self._parse_proxy_config(manual_proxies[i % len(manual_proxies)])
                self._log(f"👤 Profile {i}: Using manual proxy")
            
            profile_thread = threading.Thread(
                target=self._run_real_browser_profile,
                args=(url, i, login_google, google_email, google_password, 
                      user_agent_type, visit_duration, click_ads, proxy_config)
            )
            self.profile_threads.append(profile_thread)
            profile_thread.start()
            
            # Stagger profile starts
            delay = random.uniform(3, 8)
            time.sleep(delay)
        
        # Wait for all profiles to complete
        for thread in self.profile_threads:
            thread.join()
        
        self._log(f"✅ Real browser automation completed for {num_profiles} profiles")
    
    def _run_real_browser_profile(self, url, profile_index, login_google, google_email, 
                                google_password, user_agent_type, visit_duration, 
                                click_ads, proxy_config):
        """Run automation dengan real browser menggunakan Playwright"""
        try:
            self._log(f"👤 Profile {profile_index}: Starting real browser automation")
            
            with sync_playwright() as p:
                # Browser launch options
                launch_options = {
                    'headless': True,
                    'args': [
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor',
                        '--disable-background-timer-throttling',
                        '--disable-backgrounding-occluded-windows',
                        '--disable-renderer-backgrounding'
                    ]
                }
                
                # Add proxy if configured
                if proxy_config:
                    launch_options['proxy'] = proxy_config
                
                # Launch browser
                browser = p.chromium.launch(**launch_options)
                
                # Context options
                context_options = {
                    'viewport': {'width': 1920, 'height': 1080} if user_agent_type == 'desktop' else {'width': 390, 'height': 844},
                    'user_agent': self._get_user_agent(user_agent_type),
                    'ignore_https_errors': True
                }
                
                # Create context and page
                context = browser.new_context(**context_options)
                page = context.new_page()
                
                # Enable request interception untuk monitoring
                # page.on('request', lambda request: self._log(f"Profile {profile_index}: → {request.method} {request.url}"))
                # page.on('response', lambda response: self._log(f"Profile {profile_index}: ← {response.status} {response.url}"))
                
                try:
                    # Google login jika diminta
                    if login_google and google_email and google_password:
                        self._google_login_playwright(page, google_email, google_password, profile_index)
                    
                    # Navigate to target URL
                    self._log(f"👤 Profile {profile_index}: 🌐 Navigating to {url}")
                    page.goto(url, wait_until='domcontentloaded', timeout=30000)
                    
                    # Wait for page to load
                    page.wait_for_load_state('networkidle', timeout=10000)
                    
                    # Simulate realistic user behavior
                    self._simulate_real_behavior(page, profile_index, visit_duration)
                    
                    # Click ads jika diminta
                    if click_ads:
                        self._click_ads_playwright(page, profile_index)
                    
                    self._log(f"👤 Profile {profile_index}: ✅ Automation completed successfully")
                    
                except Exception as e:
                    self._log(f"👤 Profile {profile_index}: ❌ Error during automation - {str(e)}")
                
                finally:
                    # Close browser
                    browser.close()
                    
        except Exception as e:
            self._log(f"👤 Profile {profile_index}: 💥 Critical error - {str(e)}")
    
    def _google_login_playwright(self, page, email, password, profile_index):
        """Login ke Google account menggunakan Playwright"""
        try:
            self._log(f"👤 Profile {profile_index}: 🔐 Attempting Google login")
            
            # Go to Google login page
            page.goto('https://accounts.google.com/', wait_until='networkidle')
            
            # Fill email
            page.fill('input[type="email"]', email)
            page.click('button:has-text("Next")')
            
            # Wait for password field
            page.wait_for_selector('input[type="password"]', timeout=10000)
            
            # Fill password
            page.fill('input[type="password"]', password)
            page.click('button:has-text("Next")')
            
            # Wait for login to complete
            page.wait_for_url('**/myaccount.google.com**', timeout=15000)
            
            self._log(f"👤 Profile {profile_index}: ✅ Google login successful")
            
        except Exception as e:
            self._log(f"👤 Profile {profile_index}: ❌ Google login failed - {str(e)}")
    
    def _simulate_real_behavior(self, page, profile_index, visit_duration):
        """Simulate realistic user behavior"""
        start_time = time.time()
        behaviors = [
            ("scrolling", "📜 Scrolling down"),
            ("reading", "📖 Reading content"), 
            ("clicking", "🖱️ Clicking around"),
            ("hovering", "✨ Hovering elements"),
            ("waiting", "⏳ Waiting between actions")
        ]
        
        while time.time() - start_time < visit_duration and self.is_running:
            behavior, message = random.choice(behaviors)
            
            if behavior == "scrolling":
                # Random scroll
                scroll_amount = random.randint(300, 800)
                page.mouse.wheel(0, scroll_amount)
                self._log(f"👤 Profile {profile_index}: {message} ({scroll_amount}px)")
                
            elif behavior == "reading":
                # Simulate reading time
                read_time = random.uniform(2, 5)
                time.sleep(read_time)
                self._log(f"👤 Profile {profile_index}: {message} ({read_time:.1f}s)")
                
            elif behavior == "clicking":
                # Click on random non-dangerous elements
                try:
                    clickable_elements = page.query_selector_all('a, button, [onclick]')
                    safe_elements = [el for el in clickable_elements if self._is_safe_to_click(el)]
                    if safe_elements:
                        element = random.choice(safe_elements)
                        element.click()
                        self._log(f"👤 Profile {profile_index}: {message} on element")
                        time.sleep(2)
                except:
                    pass
                    
            elif behavior == "hovering":
                # Hover over random elements
                try:
                    all_elements = page.query_selector_all('*')
                    if all_elements:
                        element = random.choice(all_elements)
                        element.hover()
                        self._log(f"👤 Profile {profile_index}: {message}")
                except:
                    pass
            
            # Random delay between actions
            delay = random.uniform(1, 3)
            time.sleep(delay)
    
    def _click_ads_playwright(self, page, profile_index):
        """Try to click on ads"""
        try:
            self._log(f"👤 Profile {profile_index}: 🔍 Looking for ads to click")
            
            # Common ad selectors
            ad_selectors = [
                'a[href*="googleadservices"]',
                'ins.adsbygoogle',
                '[data-ad-client]',
                '[data-ad-slot]',
                '.advertisement',
                '.ad-container',
                '[id*="ad"]',
                '[class*="ad"]'
            ]
            
            for selector in ad_selectors:
                try:
                    ads = page.query_selector_all(selector)
                    if ads:
                        ad = random.choice(ads)
                        
                        # Check if ad is visible
                        if ad.is_visible():
                            ad.click()
                            self._log(f"👤 Profile {profile_index}: 🎯 Clicked ad with selector: {selector}")
                            
                            # Wait after click
                            time.sleep(random.uniform(3, 7))
                            return True
                except:
                    continue
            
            self._log(f"👤 Profile {profile_index}: ℹ️ No clickable ads found")
            
        except Exception as e:
            self._log(f"👤 Profile {profile_index}: ❌ Ad clicking error - {str(e)}")
    
    def _is_safe_to_click(self, element):
        """Check if element is safe to click"""
        try:
            tag_name = element.evaluate('el => el.tagName.toLowerCase()')
            href = element.evaluate('el => el.href || ""')
            
            # Avoid dangerous clicks
            dangerous_keywords = ['logout', 'delete', 'remove', 'disable', 'logout']
            if any(keyword in href.lower() for keyword in dangerous_keywords):
                return False
                
            return True
        except:
            return False
    
    def _get_user_agent(self, user_agent_type):
        """Get realistic user agent"""
        desktop_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]
        
        mobile_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36'
        ]
        
        if user_agent_type == 'mobile':
            return random.choice(mobile_agents)
        else:
            return random.choice(desktop_agents)
    
    def _get_premium_proxy_config(self, service, username, password):
        """Get premium proxy configuration"""
        servers = {
            'oxylabs': 'pr.oxylabs.io:7777',
            'smartproxy': 'gate.smartproxy.com:7000', 
            'brightdata': 'zproxy.lum-superproxy.io:22225',
            'netnut': 'proxy.netnut.io:10000'
        }
        
        server = servers.get(service, 'proxy-service.com:8080')
        return {
            'server': f'http://{server}',
            'username': username,
            'password': password
        }
    
    def _parse_proxy_config(self, proxy_string):
        """Parse manual proxy string into configuration"""
        try:
            if '://' in proxy_string:
                proxy_string = proxy_string.split('://', 1)[1]
            
            if '@' in proxy_string:
                auth, server = proxy_string.split('@', 1)
                username, password = auth.split(':', 1)
                return {
                    'server': f'http://{server}',
                    'username': username,
                    'password': password
                }
            else:
                return {'server': f'http://{proxy_string}'}
                
        except Exception as e:
            self._log(f"❌ Error parsing proxy: {e}")
            return None
    
    def stop_automation(self):
        """Stop automation"""
        self.is_running = False
        self._log("🛑 Automation stop requested")
    
    def _log(self, message):
        """Log message"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f'[{timestamp}] {message}\n'
        print(log_message, end='')
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message)
        except Exception as e:
            print(f'Error writing log: {e}')
    
    def get_logs(self):
        """Get logs"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f'Error reading logs: {str(e)}'def stop_automation(self):
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
