"""
Client Simulator for Irembo Secure API
This app simulates the Irembo Portal sending requests to the secure API
"""

from flask import Flask, render_template, request, jsonify, session
import requests
import hmac
import hashlib
import time
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Configuration
API_SERVER_URL = "http://localhost:5000"
CLIENT_ID = "irembo-portal"
SECRET_KEY = os.getenv("IREMBO_SECRET_KEY", "irembo-super-secret-key-2026")

# Store captured requests for replay attacks
captured_requests = []

def generate_signature(secret_key, canonical_string):
    """Generate HMAC-SHA256 signature"""
    return hmac.new(
        key=secret_key.encode('utf-8'),
        msg=canonical_string.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()

def create_canonical_string(method, path, body, timestamp, nonce):
    """Create canonical string for HMAC"""
    return f"{method}|{path}|{body}|{timestamp}|{nonce}"

@app.route('/')
def index():
    """Main client dashboard"""
    return render_template('client_dashboard.html')

@app.route('/api/send-request', methods=['POST'])
def send_request():
    """Send a request to the secure API"""
    data = request.json
    citizen_id = data.get('citizen_id', '12345')
    tamper = data.get('tamper', False)
    
    # Generate timestamp and nonce
    timestamp = str(int(time.time()))
    nonce = str(uuid.uuid4())
    
    # Create canonical string
    method = "GET"
    path = f"/api/citizen/{citizen_id}"
    body = ""  # GET requests have no body
    
    # If tampering is enabled, modify the citizen_id AFTER signature generation
    original_citizen_id = citizen_id
    if tamper:
        citizen_id = "99999"  # Attacker changes the ID!
        print(f"⚠️ ATTACK SIMULATED: Changing citizen ID from {original_citizen_id} to {citizen_id}")
    
    canonical_string = create_canonical_string(method, path, body, timestamp, nonce)
    
    # Generate signature
    signature = generate_signature(SECRET_KEY, canonical_string)
    
    # Prepare headers
    headers = {
        'X-Timestamp': timestamp,
        'X-Nonce': nonce,
        'Authorization': f'HMAC-SHA256 {signature}',
        'Content-Type': 'application/json'
    }
    
    # Send request to API server
    try:
        response = requests.get(
            f"{API_SERVER_URL}/api/citizen/{original_citizen_id if not tamper else citizen_id}",
            headers=headers
        )
        
        # Store request for potential replay
        captured = {
            'timestamp': timestamp,
            'nonce': nonce,
            'signature': signature,
            'citizen_id': original_citizen_id,
            'headers': headers,
            'time_sent': time.time()
        }
        captured_requests.append(captured)
        
        return jsonify({
            'status': 'success',
            'response_status': response.status_code,
            'response_data': response.json() if response.status_code == 200 else response.text,
            'request_details': {
                'timestamp': timestamp,
                'nonce': nonce,
                'signature': signature[:20] + '...',
                'canonical_string': canonical_string,
                'tamper_attempted': tamper
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/replay-request', methods=['POST'])
def replay_request():
    """Replay a previously captured request"""
    if not captured_requests:
        return jsonify({'status': 'error', 'message': 'No captured requests to replay'})
    
    # Get the most recent captured request
    captured = captured_requests[-1]
    
    print(f"🔄 REPLAY ATTACK: Resending request with same nonce: {captured['nonce']}")
    
    # Send the EXACT same request again (with same nonce!)
    headers = captured['headers']
    
    try:
        response = requests.get(
            f"{API_SERVER_URL}/api/citizen/{captured['citizen_id']}",
            headers=headers
        )
        
        return jsonify({
            'status': 'success',
            'response_status': response.status_code,
            'response_data': response.json() if response.status_code == 200 else response.text,
            'request_details': {
                'timestamp': captured['timestamp'],
                'nonce': captured['nonce'],
                'signature': captured['signature'][:20] + '...',
                'replay_attempted': True
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/captured-requests', methods=['GET'])
def get_captured_requests():
    """Get list of captured requests"""
    return jsonify({
        'count': len(captured_requests),
        'requests': captured_requests[-5:]  # Last 5 requests
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌐 Irembo Client Simulator Starting...")
    print(f"📍 Client will run at: http://localhost:5001")
    print(f"🔑 Using secret key: {SECRET_KEY[:8]}...")
    print(f"🎯 Target API: {API_SERVER_URL}")
    print("="*60 + "\n")
    app.run(debug=True, port=5001)