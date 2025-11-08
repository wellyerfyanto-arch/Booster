from flask import Flask, request, jsonify, render_template
import threading
import time
import os
import logging
from datetime import datetime
import uuid
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# In-memory storage
active_sessions = {}
session_logs = {}

class RealTrafficAutomation:
    def __init__(self, session_id):
        self.session_id = session_id
        self.is_running = True
        self.logs = []
    
    def log(self, message):
        """Log message dengan timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        print(log_entry)  # Print ke console Railway
        
        # Update session logs
        if self.session_id in session_logs:
            session_logs[self.session_id].append(log_entry)
        else:
            session_logs[self.session_id] = [log_entry]
    
    def run_automation(self, url, num_profiles, user_agent_type, visit_duration, click_ads):
        """MAIN automation function - FIXED"""
        try:
            self.log("🚀 STARTING REAL BROWSER AUTOMATION")
            self.log(f"📊 Parameters: {num_profiles} profiles, {visit_duration}s, {user_agent_type}")
            
            # Update session status
            if self.session_id in active_sessions:
                active_sessions[self.session_id]['status'] = 'running'
                active_sessions[self.session_id]['start_time'] = time.time()
            
            # Import Playwright inside function to avoid issues
            try:
                from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
                self.log("✅ Playwright imported successfully")
            except ImportError as e:
                self.log(f"❌ Playwright import failed: {e}")
                return
            
            profiles_completed = 0
            
            with sync_playwright() as p:
                self.log("🌐 Launching Chromium browser...")
                
                # Launch browser dengan options yang lebih robust
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor',
                        '--disable-background-timer-throttling',
                        '--disable-backgrounding-occluded-windows',
                        '--disable-renderer-backgrounding',
                        '--disable-blink-features=AutomationControlled'
                    ],
                    timeout=60000  # 60 second timeout for launch
                )
                
                self.log("✅ Browser launched successfully")
                
                for profile_index in range(num_profiles):
                    if not self.is_running:
                        self.log("🛑 Automation stopped by user")
                        break
                    
                    self.log(f"👤 Starting profile {profile_index + 1}/{num_profiles}")
                    
                    try:
                        # Create new context for each profile
                        context = browser.new_context(
                            viewport={'width': 1920, 'height': 1080} if user_agent_type == 'desktop' 
                                    else {'width': 390, 'height': 844},
                            user_agent=self.get_user_agent(user_agent_type),
                            ignore_https_errors=True
                        )
                        
                        # Anti-detection script
                        context.add_init_script("""
                            Object.defineProperty(navigator, 'webdriver', {
                                get: () => undefined,
                            });
                        """)
                        
                        page = context.new_page()
                        self.log(f"📄 Created new page for profile {profile_index + 1}")
                        
                        # Set realistic timeouts
                        page.set_default_timeout(30000)
                        page.set_default_navigation_timeout(30000)
                        
                        # **NAVIGATION - FIXED**
                        self.log(f"🌐 Profile {profile_index + 1}: Navigating to {url}")
                        
                        try:
                            # Navigate dengan multiple wait conditions
                            response = page.goto(
                                url, 
                                wait_until='networkidle',
                                timeout=45000
                            )
                            
                            if response:
                                self.log(f"✅ Profile {profile_index + 1}: Page loaded - Status {response.status}")
                            else:
                                self.log("⚠️ Profile {profile_index + 1}: No response object")
                                
                        except PlaywrightTimeoutError:
                            self.log(f"⏰ Profile {profile_index + 1}: Navigation timeout, continuing...")
                            # Continue even if timeout
                        except Exception as e:
                            self.log(f"❌ Profile {profile_index + 1}: Navigation failed - {str(e)}")
                            continue
                        
                        # Wait for page to stabilize
                        page.wait_for_timeout(2000)
                        
                        # **SCROLLING & INTERACTION - FIXED**
                        self.log(f"🎯 Profile {profile_index + 1}: Starting user interactions")
                        self.simulate_user_behavior(page, profile_index + 1, visit_duration)
                        
                        # **AD CLICKING - FIXED**
                        if click_ads:
                            self.log(f"🔍 Profile {profile_index + 1}: Looking for ads")
                            self.click_ads_improved(page, profile_index + 1)
                        
                        # Close context
                        context.close()
                        self.log(f"✅ Profile {profile_index + 1}: Context closed")
                        
                        profiles_completed += 1
                        
                        # Update progress
                        if self.session_id in active_sessions:
                            active_sessions[self.session_id]['completed_profiles'] = profiles_completed
                            active_sessions[self.session_id]['progress'] = (profiles_completed / num_profiles) * 100
                        
                        self.log(f"🎉 Profile {profile_index + 1} completed successfully")
                        
                    except Exception as e:
                        self.log(f"❌ Profile {profile_index + 1} failed: {str(e)}")
                        import traceback
                        self.log(f"🔍 Traceback: {traceback.format_exc()}")
                        continue
                
                # Close browser after all profiles
                browser.close()
                self.log("🔚 Browser closed after all profiles")
            
            self.log(f"🎊 ALL PROFILES COMPLETED: {profiles_completed}/{num_profiles}")
            
            # Update final status
            if self.session_id in active_sessions:
                active_sessions[self.session_id]['status'] = 'completed'
                active_sessions[self.session_id]['end_time'] = time.time()
            
        except Exception as e:
            error_msg = f"💥 CRITICAL ERROR: {str(e)}"
            self.log(error_msg)
            import traceback
            self.log(f"🔍 Critical traceback: {traceback.format_exc()}")
            
            if self.session_id in active_sessions:
                active_sessions[self.session_id]['status'] = f'error: {str(e)}'
                active_sessions[self.session_id]['end_time'] = time.time()
    
    def simulate_user_behavior(self, page, profile_index, visit_duration):
        """Simulate realistic user behavior dengan logging detail"""
        import random
        
        self.log(f"🎮 Profile {profile_index}: Starting behavior simulation for {visit_duration}s")
        
        start_time = time.time()
        action_count = 0
        
        try:
            # Initial scroll to ensure page is active
            page.evaluate("window.scrollTo(0, 500)")
            self.log(f"📜 Profile {profile_index}: Initial scroll")
            action_count += 1
            time.sleep(2)
            
            while time.time() - start_time < visit_duration and self.is_running:
                # Random action selection
                action_type = random.choice(['scroll', 'click', 'read', 'hover'])
                
                if action_type == 'scroll':
                    # Random scroll amount
                    scroll_y = random.randint(200, 800)
                    page.evaluate(f"window.scrollBy(0, {scroll_y})")
                    self.log(f"📜 Profile {profile_index}: Scrolled {scroll_y}px")
                    action_count += 1
                    time.sleep(random.uniform(1, 3))
                    
                elif action_type == 'click':
                    # Try to click safe elements
                    try:
                        clickable_elements = page.query_selector_all('a, button')
                        if clickable_elements:
                            safe_elements = []
                            for element in clickable_elements:
                                try:
                                    if element.is_visible():
                                        text = element.evaluate('el => el.textContent || ""')
                                        # Avoid dangerous clicks
                                        if not any(word in text.lower() for word in ['logout', 'delete', 'remove']):
                                            safe_elements.append(element)
                                except:
                                    continue
                            
                            if safe_elements:
                                element = random.choice(safe_elements)
                                element.click()
                                self.log(f"🖱️ Profile {profile_index}: Clicked element")
                                action_count += 1
                                time.sleep(3)  # Wait after click
                                
                                # Sometimes go back
                                if random.random() < 0.3:
                                    page.go_back()
                                    time.sleep(2)
                    except Exception as e:
                        self.log(f"⚠️ Profile {profile_index}: Click failed - {e}")
                
                elif action_type == 'read':
                    # Simulate reading time
                    read_time = random.uniform(3, 8)
                    self.log(f"📖 Profile {profile_index}: Reading for {read_time:.1f}s")
                    time.sleep(read_time)
                    action_count += 1
                
                elif action_type == 'hover':
                    # Hover over random elements
                    try:
                        elements = page.query_selector_all('a, button, img')
                        if elements:
                            element = random.choice(elements)
                            if element.is_visible():
                                element.hover()
                                self.log(f"✨ Profile {profile_index}: Hovered element")
                                action_count += 1
                                time.sleep(1)
                    except:
                        pass
                
                # Random delay between actions
                delay = random.uniform(1, 4)
                time.sleep(delay)
            
            self.log(f"📊 Profile {profile_index}: Completed {action_count} actions")
            
        except Exception as e:
            self.log(f"❌ Profile {profile_index}: Behavior simulation error - {e}")
    
    def click_ads_improved(self, page, profile_index):
        """Improved ad clicking dengan multiple strategies"""
        try:
            self.log(f"🔍 Profile {profile_index}: Searching for ads...")
            
            ad_selectors = [
                'a[href*="googleadservices"]',
                'ins.adsbygoogle',
                '[data-ad-client]',
                '.advertisement',
                '[class*="ad"]'
            ]
            
            for selector in ad_selectors:
                try:
                    elements = page.query_selector_all(selector)
                    self.log(f"🔎 Profile {profile_index}: Found {len(elements)} elements with {selector}")
                    
                    for element in elements:
                        if element.is_visible() and self.is_safe_to_click(element):
                            # Scroll to element first
                            element.scroll_into_view_if_needed()
                            time.sleep(1)
                            
                            # Click the element
                            element.click()
                            self.log(f"🎯 Profile {profile_index}: Clicked ad with {selector}")
                            time.sleep(5)  # Wait after click
                            return True
                            
                except Exception as e:
                    self.log(f"⚠️ Profile {profile_index}: Selector {selector} failed - {e}")
                    continue
            
            self.log(f"ℹ️ Profile {profile_index}: No clickable ads found")
            return False
            
        except Exception as e:
            self.log(f"❌ Profile {profile_index}: Ad clicking error - {e}")
            return False
    
    def is_safe_to_click(self, element):
        """Check if element is safe to click"""
        try:
            href = element.get_attribute('href') or ''
            text = element.text_content() or ''
            
            dangerous_terms = ['logout', 'delete', 'remove', 'unsubscribe']
            if any(term in href.lower() or term in text.lower() for term in dangerous_terms):
                return False
                
            return True
        except:
            return False
    
    def get_user_agent(self, user_agent_type):
        """Get realistic user agent"""
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
    
    def stop_automation(self):
        """Stop the automation"""
        self.is_running = False
        self.log("🛑 STOP SIGNAL RECEIVED")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy', 
        'timestamp': time.time(),
        'active_sessions': len(active_sessions)
    })

@app.route('/start_traffic', methods=['POST'])
def start_traffic():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        url = data.get('url', '').strip()
        num_profiles = int(data.get('num_profiles', 1))
        user_agent_type = data.get('user_agent_type', 'desktop')
        visit_duration = int(data.get('visit_duration', 30))
        click_ads = data.get('click_ads', False)
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Generate session ID
        session_id = str(uuid.uuid4())[:8]
        
        # Initialize session
        active_sessions[session_id] = {
            'status': 'starting',
            'start_time': time.time(),
            'url': url,
            'num_profiles': num_profiles,
            'user_agent_type': user_agent_type,
            'visit_duration': visit_duration,
            'click_ads': click_ads,
            'progress': 0,
            'completed_profiles': 0
        }
        
        session_logs[session_id] = []
        
        # Start automation in background thread
        def run_automation():
            automation = RealTrafficAutomation(session_id)
            automation.run_automation(
                url=url,
                num_profiles=num_profiles,
                user_agent_type=user_agent_type,
                visit_duration=visit_duration,
                click_ads=click_ads
            )
        
        thread = threading.Thread(target=run_automation)
        thread.daemon = True
        thread.start()
        
        logger.info(f"Started session {session_id} for {url}")
        
        return jsonify({
            'message': 'Real browser automation started',
            'session_id': session_id,
            'url': url,
            'num_profiles': num_profiles,
            'note': 'Check logs for detailed progress'
        })
        
    except Exception as e:
        logger.error(f"Error starting traffic: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/status/<session_id>')
def get_status(session_id):
    if session_id in active_sessions:
        return jsonify(active_sessions[session_id])
    return jsonify({'error': 'Session not found'}), 404

@app.route('/sessions')
def list_sessions():
    return jsonify({
        'active_sessions': active_sessions,
        'total': len(active_sessions)
    })

@app.route('/logs/<session_id>')
def get_logs(session_id):
    if session_id in session_logs:
        return jsonify({
            'session_id': session_id,
            'logs': '\n'.join(session_logs[session_id]),
            'status': active_sessions.get(session_id, {}).get('status', 'unknown')
        })
    return jsonify({'error': 'Session logs not found'}), 404

@app.route('/monitor')
def monitor():
    active_count = len([s for s in active_sessions.values() if s.get('status') == 'running'])
    completed_count = len([s for s in active_sessions.values() if s.get('status') == 'completed'])
    error_count = len([s for s in active_sessions.values() if 'error' in str(s.get('status'))])
    
    total_profiles = sum(s.get('completed_profiles', 0) for s in active_sessions.values())
    
    return jsonify({
        'summary': {
            'active_sessions': active_count,
            'completed_sessions': completed_count,
            'error_sessions': error_count,
            'total_sessions': len(active_sessions),
            'total_profiles_completed': total_profiles
        },
        'timestamp': time.time()
    })

@app.route('/stop_traffic/<session_id>', methods=['POST'])
def stop_traffic(session_id):
    if session_id in active_sessions:
        active_sessions[session_id]['status'] = 'stopped'
        return jsonify({'message': 'Session stopped'})
    return jsonify({'error': 'Session not found'}), 404

@app.route('/clear_completed', methods=['POST'])
def clear_completed():
    completed_sessions = []
    for session_id, data in list(active_sessions.items()):
        if data.get('status') in ['completed', 'error', 'stopped']:
            completed_sessions.append(session_id)
            del active_sessions[session_id]
    
    return jsonify({
        'cleared_sessions': completed_sessions,
        'remaining_sessions': len(active_sessions)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)