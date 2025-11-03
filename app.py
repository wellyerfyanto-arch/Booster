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

@app.route('/start_traffic', methods=['POST'])
def start_traffic():
    data = request.json
    url = data.get('url')
    session_id = data.get('session_id', 'default')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Check if session already running
    if session_id in active_sessions:
        return jsonify({'error': 'Session already running'}), 400
    
    # Start traffic automation in separate thread
    def run_automation():
        automation = TrafficAutomation()
        active_sessions[session_id] = {
            'status': 'running',
            'start_time': time.time(),
            'url': url
        }
        
        try:
            automation.run_automation(url, session_id)
            active_sessions[session_id]['status'] = 'completed'
        except Exception as e:
            active_sessions[session_id]['status'] = f'error: {str(e)}'
        finally:
            # Clean up after 5 minutes
            time.sleep(300)
            if session_id in active_sessions:
                del active_sessions[session_id]
    
    thread = threading.Thread(target=run_automation)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'message': 'Traffic automation started',
        'session_id': session_id
    })

@app.route('/status/<session_id>')
def get_status(session_id):
    if session_id in active_sessions:
        return jsonify(active_sessions[session_id])
    return jsonify({'error': 'Session not found'}), 404

@app.route('/stop_traffic/<session_id>', methods=['POST'])
def stop_traffic(session_id):
    if session_id in active_sessions:
        # In a real implementation, you'd signal the thread to stop
        del active_sessions[session_id]
        return jsonify({'message': 'Session stopped'})
    return jsonify({'error': 'Session not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
