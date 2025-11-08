from flask import Flask, request, jsonify, render_template
import threading
import time
import os
import logging
from datetime import datetime
import uuid

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# In-memory storage
active_sessions = {}
session_logs = {}

class TrafficAutomation:
    def __init__(self, session_id):
        self.session_id = session_id
        self.is_running = True
    
    def run_automation(self, url, num_profiles, visit_duration):
        """Simplified automation simulation"""
        try:
            for i in range(num_profiles):
                if not self.is_running:
                    break
                
                # Simulate profile activity
                log_message = f"Profile {i+1}: Visiting {url} for {visit_duration}s"
                self._log(session_id, log_message)
                
                # Simulate work
                time.sleep(2)
                
                # Update progress
                active_sessions[session_id]['progress'] = ((i + 1) / num_profiles) * 100
                active_sessions[session_id]['completed_profiles'] = i + 1
            
            active_sessions[session_id]['status'] = 'completed'
            self._log(session_id, "Automation completed successfully")
            
        except Exception as e:
            active_sessions[session_id]['status'] = f'error: {str(e)}'
            self._log(session_id, f"Error: {str(e)}")
    
    def stop_automation(self):
        self.is_running = False
    
    def _log(self, session_id, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        
        if session_id not in session_logs:
            session_logs[session_id] = []
        session_logs[session_id].append(log_entry)
        
        print(log_entry)

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
        visit_duration = int(data.get('visit_duration', 30))
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Generate session ID
        session_id = str(uuid.uuid4())[:8]
        
        # Initialize session
        active_sessions[session_id] = {
            'status': 'running',
            'start_time': time.time(),
            'url': url,
            'num_profiles': num_profiles,
            'visit_duration': visit_duration,
            'progress': 0,
            'completed_profiles': 0
        }
        
        session_logs[session_id] = []
        
        # Start automation in background thread
        def run_automation():
            automation = TrafficAutomation(session_id)
            automation.run_automation(url, num_profiles, visit_duration)
        
        thread = threading.Thread(target=run_automation)
        thread.daemon = True
        thread.start()
        
        logger.info(f"Started session {session_id} for {url}")
        
        return jsonify({
            'message': 'Traffic automation started',
            'session_id': session_id,
            'url': url,
            'num_profiles': num_profiles
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
    active_count = len(active_sessions)
    completed_count = len([s for s in active_sessions.values() if s.get('status') == 'completed'])
    
    return jsonify({
        'summary': {
            'active_sessions': active_count,
            'completed_sessions': completed_count,
            'total_sessions': len(active_sessions)
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
