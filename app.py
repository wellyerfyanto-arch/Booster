from flask import Flask, request, jsonify, render_template
from traffic_automation import TrafficAutomation
import threading
import time
import os

app = Flask(__name__)

# Status monitoring
active_sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': time.time()})

@app.route('/start_traffic', methods=['POST'])
def start_traffic():
    data = request.json
    url = data.get('url')
    session_id = data.get('session_id', f'session_{int(time.time())}')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Validate URL format
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Check if session already running
    if session_id in active_sessions and active_sessions[session_id]['status'] == 'running':
        return jsonify({'error': 'Session already running'}), 400
    
    # Start traffic automation in separate thread
    def run_automation():
        automation = TrafficAutomation()
        active_sessions[session_id] = {
            'status': 'running',
            'start_time': time.time(),
            'url': url,
            'last_update': time.time()
        }
        
        try:
            automation.run_automation(url, session_id)
            active_sessions[session_id].update({
                'status': 'completed',
                'end_time': time.time(),
                'last_update': time.time()
            })
        except Exception as e:
            active_sessions[session_id].update({
                'status': f'error: {str(e)}',
                'end_time': time.time(),
                'last_update': time.time()
            })
        finally:
            # Auto-cleanup after 10 minutes
            def cleanup():
                time.sleep(600)
                if session_id in active_sessions:
                    del active_sessions[session_id]
            
            cleanup_thread = threading.Thread(target=cleanup)
            cleanup_thread.daemon = True
            cleanup_thread.start()
    
    thread = threading.Thread(target=run_automation)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'message': 'Traffic automation started',
        'session_id': session_id,
        'url': url
    })

@app.route('/status/<session_id>')
def get_status(session_id):
    if session_id in active_sessions:
        active_sessions[session_id]['last_update'] = time.time()
        return jsonify(active_sessions[session_id])
    return jsonify({'error': 'Session not found'}), 404

@app.route('/sessions')
def list_sessions():
    return jsonify({
        'active_sessions': active_sessions,
        'total_sessions': len(active_sessions)
    })

@app.route('/stop_traffic/<session_id>', methods=['POST'])
def stop_traffic(session_id):
    if session_id in active_sessions:
        # In a real implementation, you'd signal the thread to stop
        active_sessions[session_id]['status'] = 'stopped_by_user'
        return jsonify({'message': 'Session stopped'})
    return jsonify({'error': 'Session not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
