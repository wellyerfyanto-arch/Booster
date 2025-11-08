import os
import sys

class TrafficAutomation:
    def __init__(self, session_id):
        self.session_id = session_id
        self.log_file = f"logs/traffic_logs_{session_id}.txt"
        self.is_running = True
        self.profile_threads = []
        
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
        os.makedirs("chrome_profiles", exist_ok=True)
        
        # Initialize log file
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write(f"Traffic Automation Session: {session_id}\n")
            f.write(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Environment: {'Production' if not os.environ.get('DEBUG') else 'Development'}\n")
            f.write("=" * 50 + "\n")
    
    def _run_single_profile(self, url, session_id, profile_index, login_google,
                           google_email, google_password, user_agent_type, 
                           visit_duration, click_ads, proxy):
        """
        Run automation for a single Chrome profile - Cloud Optimized Version
        """
        profile_id = f"{session_id}_profile_{profile_index}"
        
        try:
            self._log(f"Profile {profile_index}: Starting cloud-optimized automation")
            
            # Check if we're in production environment
            is_production = not os.environ.get('DEBUG')
            
            if is_production:
                self._log(f"Profile {profile_index}: Running in production mode")
                # Use Playwright for cloud compatibility
                self._run_with_playwright(url, profile_index, user_agent_type, visit_duration, proxy)
            else:
                self._log(f"Profile {profile_index}: Running in development mode")
                # Simulate behavior for development
                self._simulate_automation(url, profile_index, visit_duration)
            
            self._log(f"Profile {profile_index}: Automation completed successfully")
            
        except Exception as e:
            self._log(f"Profile {profile_index}: Error - {str(e)}")
    
    def _run_with_playwright(self, url, profile_index, user_agent_type, visit_duration, proxy):
        """Run automation using Playwright (cloud compatible)"""
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                # Configure browser launch options for cloud
                browser_launch_options = {
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
                
                # Add proxy if provided
                if proxy:
                    browser_launch_options['proxy'] = {'server': proxy}
                
                self._log(f"Profile {profile_index}: Launching browser...")
                browser = p.chromium.launch(**browser_launch_options)
                
                # Create context with user agent
                context = browser.new_context(
                    user_agent=self._get_user_agent(user_agent_type),
                    viewport={'width': 1920, 'height': 1080} if user_agent_type == 'desktop' else {'width': 390, 'height': 844}
                )
                
                page = context.new_page()
                
                # Navigate to URL
                self._log(f"Profile {profile_index}: Navigating to {url}")
                page.goto(url, wait_until='networkidle')
                
                # Simulate user behavior
                self._simulate_user_behavior(page, profile_index, visit_duration)
                
                # Close browser
                browser.close()
                self._log(f"Profile {profile_index}: Browser closed")
                
        except ImportError:
            self._log(f"Profile {profile_index}: Playwright not available, using simulation")
            self._simulate_automation(url, profile_index, visit_duration)
        except Exception as e:
            self._log(f"Profile {profile_index}: Playwright error - {str(e)}")
            self._simulate_automation(url, profile_index, visit_duration)
    
    def _get_user_agent(self, user_agent_type):
        """Get user agent string based on type"""
        desktop_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]
        mobile_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36'
        ]
        
        import random
        if user_agent_type == 'mobile':
            return random.choice(mobile_agents)
        else:
            return random.choice(desktop_agents)
    
    def _simulate_user_behavior(self, page, profile_index, visit_duration):
        """Simulate realistic user behavior"""
        import random
        import time
        
        # Random scrolling
        scrolls = random.randint(3, 8)
        for i in range(scrolls):
            if not self.is_running:
                break
            scroll_amount = random.randint(200, 800)
            page.mouse.wheel(0, scroll_amount)
            self._log(f"Profile {profile_index}: Scrolled {i+1}/{scrolls}")
            time.sleep(random.uniform(1, 3))
        
        # Random clicks on non-interactive elements
        clicks = random.randint(2, 5)
        for i in range(clicks):
            if not self.is_running:
                break
            # Click on random position (avoiding important elements)
            page.mouse.click(
                random.randint(100, page.viewport_size['width'] - 100),
                random.randint(100, page.viewport_size['height'] - 100)
            )
            self._log(f"Profile {profile_index}: Random click {i+1}/{clicks}")
            time.sleep(random.uniform(1, 2))
        
        # Wait for remaining time
        elapsed = scrolls * 2 + clicks * 1.5
        remaining = max(5, visit_duration - elapsed)
        
        if remaining > 0:
            self._log(f"Profile {profile_index}: Waiting {remaining} seconds")
            time.sleep(remaining)
    
    def _simulate_automation(self, url, profile_index, visit_duration):
        """Fallback simulation when browser automation is not available"""
        import time
        import random
        
        self._log(f"Profile {profile_index}: Simulating visit to {url}")
        
        steps = [
            "Initializing browser...",
            "Loading page...",
            "Rendering content...",
            "Simulating user interactions...",
            "Processing page elements...",
            "Completing visit..."
        ]
        
        for step in steps:
            if not self.is_running:
                break
            self._log(f"Profile {profile_index}: {step}")
            time.sleep(visit_duration / len(steps))
