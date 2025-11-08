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
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        print(log_entry)
        
        # Update session logs
        if self.session_id in session_logs:
            session_logs[self.session_id].append(log_entry)
    
    def run_automation(self, url, num_profiles, user_agent_type, visit_duration, click_ads, proxy_config):
        """Real browser automation dengan Playwright"""
        try:
            from playwright.sync_api import sync_playwright
            
            self.log("🚀 Starting REAL browser automation...")
            
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-dev-shm-usage',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor',
                        '--disable-background-timer-throttling',
                        '--disable-backgrounding-occluded-windows',
                        '--disable-renderer-backgrounding'
                    ]
                )
                
                profiles_completed = 0
                
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
                        
                        page = context.new_page()
                        
                        # Set longer timeouts
                        page.set_default_timeout(30000)
                        page.set_default_navigation_timeout(30000)
                        
                        # Navigate to URL
                        self.log(f"🌐 Profile {profile_index + 1}: Navigating to {url}")
                        page.goto(url, wait_until='domcontentloaded')
                        
                        # Wait for page to load
                        page.wait_for_load_state('networkidle')
                        
                        # Simulate real user behavior
                        self.simulate_user_behavior(page, profile_index, visit_duration)
                        
                        # Click ads if enabled
                        if click_ads:
                            self.click_ads(page, profile_index)
                        
                        # Close context
                        context.close()
                        
                        profiles_completed += 1
                        progress = (profiles_completed / num_profiles) * 100
                        
                        # Update session progress
                        if self.session_id in active_sessions:
                            active_sessions[self.session_id]['completed_profiles'] = profiles_completed
                            active_sessions[self.session_id]['progress'] = progress
                        
                        self.log(f"✅ Profile {profile_index + 1} completed successfully")
                        
                    except Exception as e:
                        self.log(f"❌ Profile {profile_index + 1} failed: {str(e)}")
                        continue
                
                browser.close()
                self.log("🎉 All profiles completed!")
                
                if self.session_id in active_sessions:
                    active_sessions[self.session_id]['status'] = 'completed'
                
        except Exception as e:
            error_msg = f"💥 Critical error: {str(e)}"
            self.log(error_msg)
            if self.session_id in active_sessions:
                active_sessions[self.session_id]['status'] = f'error: {str(e)}'
    
    def simulate_user_behavior(self, page, profile_index, visit_duration):
        """Simulate realistic user behavior"""
        import random
        
        self.log(f"🎯 Profile {profile_index + 1}: Simulating user behavior for {visit_duration}s")
        
        start_time = time.time()
        actions_performed = 0
        
        while time.time() - start_time < visit_duration and self.is_running:
            try:
                # Random actions
                action_type = random.choice(['scroll', 'click', 'hover', 'wait', 'read'])
                
                if action_type == 'scroll':
                    # Random scroll
                    scroll_amount = random.randint(300, 800)
                    page.mouse.wheel(0, scroll_amount)
                    self.log(f"📜 Profile {profile_index + 1}: Scrolled {scroll_amount}px")
                    actions_performed += 1
                    
                elif action_type == 'click':
                    # Try to click on safe elements
                    clickable_elements = page.query_selector_all('a, button, [onclick]')
                    safe_elements = []
                    
                    for element in clickable_elements:
                        try:
                            if element.is_visible():
                                tag_name = element.evaluate('el => el.tagName.toLowerCase()')
                                text = element.evaluate('el => el.textContent || ""').lower()
                                
                                # Avoid dangerous clicks
                                dangerous = any(word in text for word in 
                                              ['delete', 'remove', 'logout', 'unsubscribe', 'spam'])
                                if not dangerous:
                                    safe_elements.append(element)
                        except:
                            continue
                    
                    if safe_elements:
                        element = random.choice(safe_elements)
                        element.click()
                        self.log(f"🖱️ Profile {profile_index + 1}: Clicked on element")
                        actions_performed += 1
                        time.sleep(2)  # Wait after click
                
                elif action_type == 'hover':
                    # Hover over random elements
                    all_elements = page.query_selector_all('*')
                    visible_elements = [el for el in all_elements if el.is_visible()]
                    
                    if visible_elements:
                        element = random.choice(visible_elements)
                        element.hover()
                        self.log(f"✨ Profile {profile_index + 1}: Hovered over element")
                        actions_performed += 1
                
                elif action_type == 'read':
                    # Simulate reading time
                    read_time = random.uniform(3, 8)
                    time.sleep(read_time)
                    self.log(f"📖 Profile {profile_index + 1}: Reading content ({read_time:.1f}s)")
                    actions_performed += 1
                
                # Random delay between actions
                delay = random.uniform(1, 3)
                time.sleep(delay)
                
            except Exception as e:
                self.log(f"⚠️ Profile {profile_index + 1}: Action failed - {str(e)}")
                time.sleep(2)
        
        self.log(f"📊 Profile {profile_index + 1}: Completed {actions_performed} actions")
    
    def click_ads(self, page, profile_index):
        """Try to click on ads"""
        try:
            self.log(f"🔍 Profile {profile_index + 1}: Looking for ads...")
            
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
                        for ad in ads:
                            if ad.is_visible():
                                ad.click()
                                self.log(f"🎯 Profile {profile_index + 1}: Clicked ad with selector: {selector}")
                                time.sleep(5)  # Wait after click
                                return True
                except:
                    continue
            
            self.log(f"ℹ️ Profile {profile_index + 1}: No clickable ads found")
            
        except Exception as e:
            self.log(f"❌ Profile {profile_index + 1}: Ad clicking failed - {str(e)}")
    
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
        self.is_running = False
        self.log("🛑 Stop signal received")

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
            'status': 'running',
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
                click_ads=click_ads,
                proxy_config=None  # bisa ditambahkan later
            )
        
        thread = threading.Thread(target=run_automation)
        thread.daemon = True
        thread.start()
        
        logger.info(f"Started REAL browser session {session_id} for {url}")
        
        return jsonify({
            'message': 'Real browser automation started',
            'session_id': session_id,
            'url': url,
            'num_profiles': num_profiles,
            'type': 'REAL_BROWSER'
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
