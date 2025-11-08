from flask import Flask, request, jsonify, render_template, send_file
from traffic_automation import TrafficAutomation
import threading
import time
import os
import logging
from datetime import datetime
import json
import re
# Untuk production di Render
import os
# Untuk production di Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Debug mode hanya di local
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Jika di production (Render), gunakan host 0.0.0.0
    if 'RENDER' in os.environ:
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        app.run(host='0.0.0.0', port=port, debug=debug_mode)
# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Status monitoring
active_sessions = {}
session_logs = {}

def validate_proxy_format(proxy):
    """Validate proxy format"""
    try:
        # Support formats: 
        # - ip:port
        # - user:pass@ip:port
        # - http://user:pass@ip:port
        # - https://user:pass@ip:port
        if '://' in proxy:
            proxy = proxy.split('://', 1)[1]
        
        if '@' in proxy:
            auth_part, server_part = proxy.split('@', 1)
            if ':' not in auth_part:
                return False
        else:
            server_part = proxy
        
        if ':' not in server_part:
            return False
            
        ip_port = server_part.split(':')
        if len(ip_port) != 2:
            return False
            
        ip, port = ip_port
        if not port.isdigit():
            return False
        port_num = int(port)
        if port_num < 1 or port_num > 65535:
            return False
            
        # Basic IP validation
        ip_parts = ip.split('.')
        if len(ip_parts) != 4:
            return False
        for part in ip_parts:
            if not part.isdigit() or int(part) < 0 or int(part) > 255:
                return False
                
        return True
    except:
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy', 
        'timestamp': time.time(),
        'active_sessions': len(active_sessions),
        'total_sessions': len(session_logs)
    })

@app.route('/start_traffic', methods=['POST'])
def start_traffic():
    data = request.json
    url = data.get('url', '').strip()
    session_id = data.get('session_id', f'session_{int(time.time())}')
    
    # New parameters
    num_profiles = data.get('num_profiles', 1)
    login_google = data.get('login_google', False)
    google_email = data.get('google_email', '')
    google_password = data.get('google_password', '')
    user_agent_type = data.get('user_agent_type', 'desktop')  # 'desktop' or 'mobile'
    visit_duration = data.get('visit_duration', 30)  # in seconds
    click_ads = data.get('click_ads', False)
    
    # Proxy parameters
    proxy_type = data.get('proxy_type', 'none')  # 'none', 'premium', 'manual'
    premium_proxy_service = data.get('premium_proxy_service', '')  # e.g., 'oxylabs', 'smartproxy'
    premium_proxy_username = data.get('premium_proxy_username', '')
    premium_proxy_password = data.get('premium_proxy_password', '')
    manual_proxies_text = data.get('manual_proxies', '')
    
    # Parse manual proxies from text
    manual_proxies = []
    if manual_proxies_text:
        manual_proxies = [proxy.strip() for proxy in manual_proxies_text.split('\n') if proxy.strip()]
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Validate and format URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Basic URL validation
    if not '.' in url.replace('//', ''):
        return jsonify({'error': 'Invalid URL format'}), 400
    
    # Validate number of profiles
    if not isinstance(num_profiles, int) or num_profiles < 1 or num_profiles > 50:
        return jsonify({'error': 'Number of profiles must be between 1 and 50'}), 400
    
    # Validate visit duration
    if not isinstance(visit_duration, int) or visit_duration < 5 or visit_duration > 3600:
        return jsonify({'error': 'Visit duration must be between 5 and 3600 seconds'}), 400
    
    # Validate Google login credentials if login is requested
    if login_google and (not google_email or not google_password):
        return jsonify({'error': 'Google email and password are required when login_google is enabled'}), 400
    
    # Validate proxy settings
    if proxy_type == 'premium':
        if not premium_proxy_service:
            return jsonify({'error': 'Premium proxy service is required when using premium proxies'}), 400
        if not premium_proxy_username or not premium_proxy_password:
            return jsonify({'error': 'Premium proxy username and password are required'}), 400
    
    elif proxy_type == 'manual':
        if not manual_proxies:
            return jsonify({'error': 'Manual proxies list is required when using manual proxies'}), 400
        if len(manual_proxies) < num_profiles:
            return jsonify({'error': f'Number of manual proxies ({len(manual_proxies)}) must be at least equal to number of profiles ({num_profiles})'}), 400
        
        # Validate proxy format for each proxy
        for proxy in manual_proxies:
            if not validate_proxy_format(proxy):
                return jsonify({'error': f'Invalid proxy format: {proxy}. Expected format: ip:port or user:pass@ip:port'}), 400
    
    # Check if session already running
    if session_id in active_sessions:
        session_data = active_sessions[session_id]
        if session_data.get('status') == 'running':
            return jsonify({'error': 'Session already running'}), 400
    
    # Start traffic automation in separate thread
    def run_automation():
        automation = TrafficAutomation(session_id)
        active_sessions[session_id] = {
            'status': 'running',
            'start_time': time.time(),
            'url': url,
            'last_update': time.time(),
            'iterations_completed': 0,
            'automation': automation,
            'parameters': {
                'num_profiles': num_profiles,
                'login_google': login_google,
                'user_agent_type': user_agent_type,
                'visit_duration': visit_duration,
                'click_ads': click_ads,
                'proxy_type': proxy_type,
                'premium_proxy_service': premium_proxy_service,
                'manual_proxies_count': len(manual_proxies)
            }
        }
        
        # Initialize logs
        session_logs[session_id] = {
            'start_time': datetime.now().isoformat(),
            'logs': [],
            'status': 'running',
            'parameters': {
                'num_profiles': num_profiles,
                'login_google': login_google,
                'user_agent_type': user_agent_type,
                'visit_duration': visit_duration,
                'click_ads': click_ads,
                'proxy_type': proxy_type,
                'premium_proxy_service': premium_proxy_service
            }
        }
        
        try:
            # Pass all parameters to the automation
            automation.run_automation(
                url, 
                session_id,
                num_profiles=num_profiles,
                login_google=login_google,
                google_email=google_email,
                google_password=google_password,
                user_agent_type=user_agent_type,
                visit_duration=visit_duration,
                click_ads=click_ads,
                proxy_type=proxy_type,
                premium_proxy_service=premium_proxy_service,
                premium_proxy_username=premium_proxy_username,
                premium_proxy_password=premium_proxy_password,
                manual_proxies=manual_proxies
            )
            active_sessions[session_id].update({
                'status': 'completed',
                'end_time': time.time(),
                'last_update': time.time(),
                'iterations_completed': num_profiles
            })
            session_logs[session_id]['status'] = 'completed'
            session_logs[session_id]['end_time'] = datetime.now().isoformat()
            session_logs[session_id]['iterations_completed'] = num_profiles
            
        except Exception as e:
            error_msg = str(e)
            active_sessions[session_id].update({
                'status': f'error: {error_msg}',
                'end_time': time.time(), 
                'last_update': time.time()
            })
            session_logs[session_id]['status'] = f'error: {error_msg}'
            session_logs[session_id]['end_time'] = datetime.now().isoformat()
            logger.error(f"Session {session_id} failed: {error_msg}")
            
        finally:
            # Auto-cleanup after 10 minutes for completed/error sessions
            def cleanup():
                time.sleep(600)
                if session_id in active_sessions and active_sessions[session_id]['status'] in ['completed', 'error']:
                    # Save logs before cleanup
                    try:
                        log_content = automation.get_logs()
                        session_logs[session_id]['log_content'] = log_content
                    except Exception as e:
                        logger.error(f"Failed to save logs for session {session_id}: {e}")
                    del active_sessions[session_id]
                    logger.info(f"Cleaned up session: {session_id}")
            
            cleanup_thread = threading.Thread(target=cleanup)
            cleanup_thread.daemon = True
            cleanup_thread.start()
    
    thread = threading.Thread(target=run_automation)
    thread.daemon = True
    thread.start()
    
    logger.info(f"Started traffic session {session_id} for {url} with {num_profiles} profiles, proxy_type: {proxy_type}")
    
    return jsonify({
        'message': 'Traffic automation started successfully',
        'session_id': session_id,
        'url': url,
        'parameters': {
            'num_profiles': num_profiles,
            'login_google': login_google,
            'user_agent_type': user_agent_type,
            'visit_duration': visit_duration,
            'click_ads': click_ads,
            'proxy_type': proxy_type,
            'premium_proxy_service': premium_proxy_service,
            'manual_proxies_count': len(manual_proxies)
        },
        'note': 'Proxy rotation enabled' if proxy_type != 'none' else 'No proxy used'
    })

@app.route('/status/<session_id>')
def get_status(session_id):
    if session_id in active_sessions:
        session_data = active_sessions[session_id]
        session_data['last_update'] = time.time()
        
        # Calculate progress based on iterations
        total_iterations = session_data['parameters']['num_profiles']
        completed_iterations = session_data.get('iterations_completed', 0)
        progress = (completed_iterations / total_iterations) * 100 if total_iterations > 0 else 0
        
        response_data = session_data.copy()
        response_data['progress'] = round(progress, 2)
        response_data['completed_iterations'] = completed_iterations
        response_data['total_iterations'] = total_iterations
        
        return jsonify(response_data)
    return jsonify({'error': 'Session not found'}), 404

@app.route('/sessions')
def list_sessions():
    sessions_info = {}
    for session_id, data in active_sessions.items():
        sessions_info[session_id] = {
            'status': data['status'],
            'url': data['url'],
            'start_time': data['start_time'],
            'last_update': data['last_update'],
            'iterations_completed': data.get('iterations_completed', 0),
            'parameters': data.get('parameters', {})
        }
    
    return jsonify({
        'active_sessions': sessions_info,
        'total_active': len(active_sessions),
        'total_historical': len(session_logs)
    })

@app.route('/logs/<session_id>')
def get_logs(session_id):
    """Get logs for a specific session"""
    if session_id in active_sessions:
        try:
            automation = active_sessions[session_id].get('automation')
            if automation:
                logs = automation.get_logs()
                return jsonify({
                    'session_id': session_id,
                    'logs': logs,
                    'status': 'active'
                })
        except Exception as e:
            logger.error(f"Error getting logs for active session {session_id}: {e}")
    
    # Check historical logs
    if session_id in session_logs:
        logs = session_logs[session_id].get('log_content', 'Logs not available')
        return jsonify({
            'session_id': session_id,
            'logs': logs,
            'status': session_logs[session_id].get('status', 'unknown'),
            'iterations_completed': session_logs[session_id].get('iterations_completed', 0)
        })
    
    return jsonify({'error': 'Session logs not found'}), 404

@app.route('/logs/<session_id>/download')
def download_logs(session_id):
    """Download log file for a session"""
    if session_id in active_sessions:
        try:
            automation = active_sessions[session_id].get('automation')
            if automation:
                log_file = automation.log_file
                if os.path.exists(log_file):
                    return send_file(log_file, as_attachment=True, download_name=f"traffic_logs_{session_id}.txt")
        except Exception as e:
            logger.error(f"Error downloading logs for session {session_id}: {e}")
    
    # Check if we have logs in session_logs
    if session_id in session_logs and 'log_content' in session_logs[session_id]:
        try:
            # Create temporary file
            temp_log_file = f"/tmp/traffic_logs_{session_id}.txt"
            with open(temp_log_file, 'w', encoding='utf-8') as f:
                f.write(session_logs[session_id]['log_content'])
            return send_file(temp_log_file, as_attachment=True, download_name=f"traffic_logs_{session_id}.txt")
        except Exception as e:
            logger.error(f"Error creating temp log file for session {session_id}: {e}")
    
    return jsonify({'error': 'Log file not found'}), 404

@app.route('/monitor')
def monitor():
    """Monitor dashboard"""
    active_count = len(active_sessions)
    completed_count = len([s for s in session_logs.values() if s.get('status') == 'completed'])
    error_count = len([s for s in session_logs.values() if 'error' in str(s.get('status'))])
    running_count = len([s for s in session_logs.values() if s.get('status') == 'running'])
    
    # Calculate total iterations across all sessions
    total_iterations = sum(s.get('iterations_completed', 0) for s in session_logs.values())
    
    recent_sessions = []
    for session_id, data in list(session_logs.items())[-10:]:  # Last 10 sessions
        recent_sessions.append({
            'session_id': session_id,
            'status': data.get('status', 'unknown'),
            'start_time': data.get('start_time'),
            'end_time': data.get('end_time'),
            'iterations_completed': data.get('iterations_completed', 0),
            'parameters': data.get('parameters', {})
        })
    
    return jsonify({
        'summary': {
            'active_sessions': active_count,
            'completed_sessions': completed_count,
            'error_sessions': error_count,
            'running_sessions': running_count,
            'total_sessions': len(session_logs),
            'total_iterations': total_iterations
        },
        'recent_sessions': recent_sessions,
        'timestamp': time.time()
    })

@app.route('/stop_traffic/<session_id>', methods=['POST'])
def stop_traffic(session_id):
    if session_id in active_sessions:
        active_sessions[session_id]['status'] = 'stopped_by_user'
        session_logs[session_id]['status'] = 'stopped_by_user'
        
        # Try to stop the automation
        try:
            automation = active_sessions[session_id].get('automation')
            if automation:
                automation.stop_automation()
        except:
            pass
            
        return jsonify({'message': 'Session stopped successfully'})
    return jsonify({'error': 'Session not found'}), 404

@app.route('/clear_completed', methods=['POST'])
def clear_completed():
    """Clear completed sessions"""
    completed_sessions = []
    for session_id, data in list(active_sessions.items()):
        if data['status'] in ['completed', 'error', 'stopped_by_user']:
            completed_sessions.append(session_id)
            del active_sessions[session_id]
    
    return jsonify({
        'cleared_sessions': completed_sessions,
        'remaining_sessions': len(active_sessions)
    })

@app.route('/clear_all_sessions', methods=['POST'])
def clear_all_sessions():
    """Clear all sessions (active and historical)"""
    active_count = len(active_sessions)
    historical_count = len(session_logs)
    
    active_sessions.clear()
    session_logs.clear()
    
    return jsonify({
        'message': 'All sessions cleared',
        'cleared_active': active_count,
        'cleared_historical': historical_count
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
