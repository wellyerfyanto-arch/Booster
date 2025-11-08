import threading
import time
import os
import random
from datetime import datetime
import logging
from playwright.sync_api import sync_playwright
import requests

logger = logging.getLogger(__name__)

class RealTrafficAutomation:
    def __init__(self, session_id):
        self.session_id = session_id
        self.is_running = True
        self.logs = []
    
    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        print(log_entry)
        
        if self.session_id in session_logs:
            session_logs[self.session_id].append(log_entry)
    
    def run_automation(self, url, num_profiles, user_agent_type, visit_duration, click_ads, proxy_config):
        """Real browser automation dengan improvements untuk GA"""
        try:
            from playwright.sync_api import sync_playwright
            
            self.log("🚀 Starting REAL browser automation with GA improvements...")
            
            profiles_completed = 0
            
            for profile_index in range(num_profiles):
                if not self.is_running:
                    self.log("🛑 Automation stopped by user")
                    break
                
                self.log(f"👤 Starting profile {profile_index + 1}/{num_profiles}")
                
                try:
                    with sync_playwright() as p:
                        # Launch browser dengan settings improved
                        browser = p.chromium.launch(
                            headless=True,  # Ganti ke False jika mau lihat browser
                            args=[
                                '--no-sandbox',
                                '--disable-dev-shm-usage',
                                '--disable-gpu',
                                '--disable-web-security',
                                '--disable-features=VizDisplayCompositor',
                                '--disable-background-timer-throttling',
                                '--disable-backgrounding-occluded-windows',
                                '--disable-renderer-backgrounding',
                                '--disable-blink-features=AutomationControlled',
                                '--user-agent=' + self.get_user_agent(user_agent_type)
                            ]
                        )
                        
                        # Create context dengan settings realistic
                        context = browser.new_context(
                            viewport={'width': 1920, 'height': 1080} if user_agent_type == 'desktop' 
                                    else {'width': 390, 'height': 844},
                            user_agent=self.get_user_agent(user_agent_type),
                            ignore_https_errors=True,
                            # Tambahkan geographic settings
                            locale='en-US',
                            timezone_id='America/New_York'
                        )
                        
                        # Add random cookies untuk simulasi user returning
                        context.add_init_script("""
                            Object.defineProperty(navigator, 'webdriver', {
                                get: () => undefined,
                            });
                        """)
                        
                        page = context.new_page()
                        
                        # Set realistic timeouts
                        page.set_default_timeout(45000)
                        page.set_default_navigation_timeout(45000)
                        
                        # **FIX 1: Navigate dengan wait untuk GA loading**
                        self.log(f"🌐 Profile {profile_index + 1}: Navigating to {url}")
                        
                        # Pertama, buka halaman dengan referrer dari Google
                        await page.evaluate_on_new_document("""
                            Object.defineProperty(document, 'referrer', {
                                get: () => 'https://www.google.com/'
                            });
                        """)
                        
                        # Navigate ke target URL
                        page.goto(url, wait_until='networkidle', timeout=45000)
                        
                        # **FIX 2: Tunggu GA script load**
                        self.wait_for_ga_scripts(page, profile_index)
                        
                        # **FIX 3: Simulasi behavior yang lebih natural**
                        self.simulate_natural_behavior(page, profile_index, visit_duration)
                        
                        # **FIX 4: Improved ad clicking**
                        if click_ads:
                            self.click_ads_improved(page, profile_index)
                        
                        # **FIX 5: Kunjungi multiple pages dalam website**
                        self.visit_internal_pages(page, profile_index, url)
                        
                        # **FIX 6: Scroll dan interaction natural**
                        self.natural_scroll_behavior(page, profile_index)
                        
                        # Close browser
                        browser.close()
                        
                        profiles_completed += 1
                        progress = (profiles_completed / num_profiles) * 100
                        
                        if self.session_id in active_sessions:
                            active_sessions[self.session_id]['completed_profiles'] = profiles_completed
                            active_sessions[self.session_id]['progress'] = progress
                        
                        self.log(f"✅ Profile {profile_index + 1} completed successfully")
                        
                except Exception as e:
                    self.log(f"❌ Profile {profile_index + 1} failed: {str(e)}")
                    continue
            
            self.log("🎉 All profiles completed!")
            
            if self.session_id in active_sessions:
                active_sessions[self.session_id]['status'] = 'completed'
                
        except Exception as e:
            error_msg = f"💥 Critical error: {str(e)}"
            self.log(error_msg)
            if self.session_id in active_sessions:
                active_sessions[self.session_id]['status'] = f'error: {str(e)}'
    
    def wait_for_ga_scripts(self, page, profile_index):
        """Wait untuk Google Analytics scripts load"""
        try:
            self.log(f"📊 Profile {profile_index + 1}: Waiting for analytics scripts...")
            
            # Wait untuk common GA scripts
            ga_selectors = [
                'script[src*="google-analytics"]',
                'script[src*="gtag"]',
                'script[src*="ga.js"]',
                'script[src*="analytics"]'
            ]
            
            for selector in ga_selectors:
                try:
                    page.wait_for_selector(selector, timeout=10000)
                    self.log(f"✅ Profile {profile_index + 1}: Found {selector}")
                except:
                    continue
            
            # Tunggu sedikit untuk GA initialize
            time.sleep(3)
            
        except Exception as e:
            self.log(f"⚠️ Profile {profile_index + 1}: GA wait issue - {str(e)}")
    
    def simulate_natural_behavior(self, page, profile_index, visit_duration):
        """Simulasi behavior yang lebih natural untuk GA"""
        import random
        
        self.log(f"🎯 Profile {profile_index + 1}: Natural behavior simulation for {visit_duration}s")
        
        start_time = time.time()
        actions = [
            ("reading", "📖 Reading content", (5, 12)),
            ("scrolling", "📜 Scrolling through page", (3, 8)),
            ("clicking", "🖱️ Clicking on content", (2, 5)),
            ("hovering", "✨ Hovering over elements", (1, 3)),
            ("video_watch", "🎥 Watching embedded content", (10, 25)),
            ("form_interaction", "📝 Interacting with forms", (3, 7))
        ]
        
        time_spent = 0
        
        while time.time() - start_time < visit_duration and self.is_running:
            try:
                # Pilih random action
                action_type, message, time_range = random.choice(actions)
                action_time = random.uniform(time_range[0], time_range[1])
                
                self.log(f"{message} for {action_time:.1f}s")
                
                if action_type == "reading":
                    # Simulate reading behavior
                    self.simulate_reading(page, action_time)
                    
                elif action_type == "scrolling":
                    # Natural scroll pattern
                    self.natural_scroll_behavior(page, profile_index)
                    
                elif action_type == "clicking":
                    # Click on content links
                    self.click_content_links(page, profile_index)
                    
                elif action_type == "hovering":
                    # Hover on interactive elements
                    self.hover_elements(page, profile_index)
                    
                elif action_type == "video_watch":
                    # Simulate video watching
                    time.sleep(action_time)
                    
                elif action_type == "form_interaction":
                    # Interact with forms
                    self.interact_with_forms(page, profile_index)
                
                time_spent += action_time
                
                # Random pause between actions
                pause_time = random.uniform(1, 4)
                time.sleep(pause_time)
                
            except Exception as e:
                self.log(f"⚠️ Profile {profile_index + 1}: Behavior simulation failed - {str(e)}")
                time.sleep(2)
        
        self.log(f"📊 Profile {profile_index + 1}: Spent {time_spent:.1f}s on natural behaviors")
    
    def natural_scroll_behavior(self, page, profile_index):
        """Natural scrolling pattern"""
        try:
            scroll_patterns = [
                [200, 400, 300, -200, 500],  # Slow reader
                [800, 400, 600, 300, 200],   # Quick scanner
                [150, 300, 450, 600, 400]    # Methodical reader
            ]
            
            pattern = random.choice(scroll_patterns)
            
            for scroll_amount in pattern:
                if not self.is_running:
                    break
                    
                page.mouse.wheel(0, scroll_amount)
                time.sleep(random.uniform(0.5, 1.5))
                
        except Exception as e:
            self.log(f"⚠️ Profile {profile_index + 1}: Scroll failed - {str(e)}")
    
    def click_content_links(self, page, profile_index):
        """Click pada content links yang aman"""
        try:
            # Cari links yang natural untuk di-click
            content_links = page.query_selector_all('a:not([href*="logout"]):not([href*="delete"]):not([href*="admin"])')
            
            if content_links:
                safe_links = []
                for link in content_links:
                    try:
                        if link.is_visible() and self.is_safe_link(link):
                            safe_links.append(link)
                    except:
                        continue
                
                if safe_links:
                    link = random.choice(safe_links)
                    link_text = link.evaluate('el => el.textContent || ""').strip()[:50]
                    link.click()
                    self.log(f"🔗 Profile {profile_index + 1}: Clicked link: {link_text}")
                    
                    # Tunggu page load
                    page.wait_for_load_state('networkidle')
                    time.sleep(random.uniform(2, 5))
                    
                    # Kembali ke previous page 50% of the time
                    if random.random() < 0.5:
                        page.go_back()
                        page.wait_for_load_state('networkidle')
                    
        except Exception as e:
            self.log(f"⚠️ Profile {profile_index + 1}: Link click failed - {str(e)}")
    
    def is_safe_link(self, element):
        """Check jika link aman untuk di-click"""
        try:
            href = element.evaluate('el => el.href || ""')
            text = element.evaluate('el => el.textContent || ""').lower()
            
            dangerous_terms = ['logout', 'delete', 'remove', 'unsubscribe', 'spam', 'admin']
            if any(term in href.lower() or term in text for term in dangerous_terms):
                return False
                
            return True
        except:
            return False
    
    def click_ads_improved(self, page, profile_index):
        """Improved ad clicking mechanism"""
        try:
            self.log(f"🔍 Profile {profile_index + 1}: Looking for ads...")
            
            # Tunggu untuk ads load
            time.sleep(3)
            
            # Multiple ad detection strategies
            ad_strategies = [
                self.click_google_ads,
                self.click_banner_ads,
                self.click_text_ads
            ]
            
            ads_clicked = 0
            max_ads_to_click = random.randint(1, 2)  # Click 1-2 ads saja
            
            for strategy in ad_strategies:
                if ads_clicked >= max_ads_to_click:
                    break
                    
                if strategy(page, profile_index):
                    ads_clicked += 1
                    time.sleep(random.uniform(5, 10))  # Wait after ad click
            
            if ads_clicked == 0:
                self.log(f"ℹ️ Profile {profile_index + 1}: No ads found to click")
            else:
                self.log(f"🎯 Profile {profile_index + 1}: Clicked {ads_clicked} ads")
                
        except Exception as e:
            self.log(f"❌ Profile {profile_index + 1}: Ad clicking failed - {str(e)}")
    
    def click_google_ads(self, page, profile_index):
        """Click Google Ads specifically"""
        try:
            # Google Ads selectors
            google_ad_selectors = [
                'ins.adsbygoogle',
                '[data-ad-client]',
                '[data-ad-slot]',
                'a[href*="googleadservices"]',
                'a[href*="doubleclick.net"]'
            ]
            
            for selector in google_ad_selectors:
                try:
                    ads = page.query_selector_all(selector)
                    for ad in ads:
                        if ad.is_visible() and ad.is_enabled():
                            # Scroll ke ad dulu
                            ad.scroll_into_view_if_needed()
                            time.sleep(1)
                            
                            ad.click()
                            self.log(f"✅ Profile {profile_index + 1}: Clicked Google ad")
                            return True
                except:
                    continue
            return False
        except:
            return False
    
    def visit_internal_pages(self, page, profile_index, base_url):
        """Kunjungi internal pages untuk meningkatkan session duration"""
        try:
            if random.random() < 0.7:  # 70% chance untuk visit internal pages
                internal_links = page.query_selector_all('a[href^="/"], a[href*="' + base_url + '"]')
                
                if internal_links:
                    safe_internal_links = []
                    for link in internal_links:
                        if self.is_safe_link(link) and link.is_visible():
                            safe_internal_links.append(link)
                    
                    if safe_internal_links:
                        # Visit 1-3 internal pages
                        pages_to_visit = random.randint(1, min(3, len(safe_internal_links)))
                        
                        for i in range(pages_to_visit):
                            if not self.is_running:
                                break
                                
                            link = random.choice(safe_internal_links)
                            link_text = link.evaluate('el => el.textContent || ""').strip()[:30]
                            
                            self.log(f"🏠 Profile {profile_index + 1}: Visiting internal page: {link_text}")
                            link.click()
                            
                            # Tunggu page load
                            page.wait_for_load_state('networkidle')
                            time.sleep(random.uniform(3, 8))
                            
                            # Scroll di halaman baru
                            self.natural_scroll_behavior(page, profile_index)
                            
                            # Kembali ke halaman sebelumnya atau stay
                            if random.random() < 0.5 and i < pages_to_visit - 1:
                                page.go_back()
                                page.wait_for_load_state('networkidle')
                        
                        self.log(f"🔗 Profile {profile_index + 1}: Visited {pages_to_visit} internal pages")
                        
        except Exception as e:
            self.log(f"⚠️ Profile {profile_index + 1}: Internal pages visit failed - {str(e)}")
    
    def get_user_agent(self, user_agent_type):
        """Get realistic user agents"""
        desktop_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]
        
        mobile_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36'
        ]
        
        import random
        if user_agent_type == 'mobile':
            return random.choice(mobile_agents)
        else:
            return random.choice(desktop_agents)
    
    def stop_automation(self):
        self.is_running = False
        self.log("🛑 Stop signal received")

# Update session_logs dan active_sessions di app.py
session_logs = {}
active_sessions = {}
