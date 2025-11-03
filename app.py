from flask import Flask, request, jsonify, render_template, send_file
from traffic_automation import TrafficAutomation
import threading
import time
import os
import logging
from datetime import datetime
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Status monitoring
active_sessions = {}
session_logs = {}

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
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Validate and format URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Basic URL validation
    if not '.' in url.replace('//', ''):
        return jsonify({'error': 'Invalid URL format'}), 400
    
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
            'automation': automation
        }
        
        # Initialize logs
        session_logs[session_id] = {
            'start_time': datetime.now().isoformat(),
            'logs': [],
            'status': 'running'
        }
        
        try:
            automation.run_automation(url, session_id)
            active_sessions[session_id].update({
                'status': 'completed',
                'end_time': time.time(),
                'last_update': time.time(),
                'iterations_completed': 2
            })
            session_logs[session_id]['status'] = 'completed'
            session_logs[session_id]['end_time'] = datetime.now().isoformat()
            
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
            # Auto-cleanup after 10 minutes
            def cleanup():
                time.sleep(600)
                if session_id in active_sessions:
                    # Save logs before cleanup
                    try:
                        log_content = automation.get_logs()
                        session_logs[session_id]['log_content'] = log_content
                    except:
                        pass
                    del active_sessions[session_id]
                    logger.info(f"Cleaned up session: {session_id}")
            
            cleanup_thread = threading.Thread(target=cleanup)
            cleanup_thread.daemon = True
            cleanup_thread.start()
    
    thread = threading.Thread(target=run_automation)
    thread.daemon = True
    thread.start()
    
    logger.info(f"Started traffic session {session_id} for {url}")
    
    return jsonify({
        'message': 'Traffic automation started successfully',
        'session_id': session_id,
        'url': url,
        'note': 'Proxy rotation enabled from multiple sources'
    })

@app.route('/status/<session_id>')
def get_status(session_id):
    if session_id in active_sessions:
        active_sessions[session_id]['last_update'] = time.time()
        return jsonify(active_sessions[session_id])
    return jsonify({'error': 'Session not found'}), 404

@app.route('/sessions')
def list_sessions():
    sessions_info = {}
    for session_id, data in active_sessions.items():
        sessions_info[session_id] = {
            'status': data['status'],
            'url': data['url'],
            'start_time': data['start_time'],
            'last_update': data['last_update']
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
        except:
            pass
    
    # Check historical logs
    if session_id in session_logs:
        logs = session_logs[session_id].get('log_content', 'Logs not available')
        return jsonify({
            'session_id': session_id,
            'logs': logs,
            'status': session_logs[session_id].get('status', 'unknown')
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
                return send_file(log_file, as_attachment=True, download_name=f"traffic_logs_{session_id}.txt")
        except:
            pass
    
    return jsonify({'error': 'Log file not found'}), 404

@app.route('/monitor')
def monitor():
    """Monitor dashboard"""
    active_count = len(active_sessions)
    completed_count = len([s for s in session_logs.values() if s.get('status') == 'completed'])
    error_count = len([s for s in session_logs.values() if 'error' in str(s.get('status'))])
    
    recent_sessions = []
    for session_id, data in list(session_logs.items())[-10:]:  # Last 10 sessions
        recent_sessions.append({
            'session_id': session_id,
            'status': data.get('status', 'unknown'),
            'start_time': data.get('start_time'),
            'end_time': data.get('end_time')
        })
    
    return jsonify({
        'summary': {
            'active_sessions': active_count,
            'completed_sessions': completed_count,
            'error_sessions': error_count,
            'total_sessions': len(session_logs)
        },
        'recent_sessions': recent_sessions,
        'timestamp': time.time()
    })

@app.route('/stop_traffic/<session_id>', methods=['POST'])
def stop_traffic(session_id):
    if session_id in active_sessions:
        active_sessions[session_id]['status'] = 'stopped_by_user'
        session_logs[session_id]['status'] = 'stopped_by_user'
        return jsonify({'message': 'Session stopped'})
    return jsonify({'error': 'Session not found'}), 404

@app.route('/clear_completed', methods=['POST'])
def clear_completed():
    """Clear completed sessions"""
    completed_sessions = []
    for session_id, data in list(active_sessions.items()):
        if data['status'] in ['completed', 'error']:
            completed_sessions.append(session_id)
            del active_sessions[session_id]
    
    return jsonify({
        'cleared_sessions': completed_sessions,
        'remaining_sessions': len(active_sessions)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
