"""
Irembo Secure API - Main Server Application
Now with full HMAC authentication!
"""

from flask import Flask, jsonify, request
import os
from datetime import datetime
import json

# Import our middleware modules
from middleware.timestamp_validator import TimestampValidator
from middleware.nonce_manager import NonceManager
from middleware.hmac_verifier import HMACVerifier

app = Flask(__name__)

# Initialize middleware components
print("\n" + "="*60)
print("🚀 INITIALIZING IREMOBO SECURE API")
print("="*60)

timestamp_validator = TimestampValidator()
nonce_manager = NonceManager()
hmac_verifier = HMACVerifier()

print("="*60 + "\n")

# Simple in-memory database
citizen_database = {
    "12345": {"id": "12345", "name": "Uwase Diane", "sector": "Gasabo", "age": 32},
    "67890": {"id": "67890", "name": "Mugisha Jean", "sector": "Nyarugenge", "age": 28},
    "11121": {"id": "11121", "name": "Mukamana Alice", "sector": "Kicukiro", "age": 45}
}

def create_canonical_string(method, path, body, timestamp, nonce):
    """
    Create canonical string for HMAC verification
    Format: METHOD|PATH|BODY|TIMESTAMP|NONCE
    """
    return f"{method}|{path}|{body}|{timestamp}|{nonce}"

@app.before_request
def log_request_info():
    """Log all incoming requests (helpful for debugging)"""
    print(f"\n📥 Incoming Request: {request.method} {request.path}")
    print(f"   Headers: {dict(request.headers)}")
    if request.data:
        print(f"   Body: {request.data.decode('utf-8')}")

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "Irembo Secure API is running with HMAC authentication!"
    })

@app.route('/api/citizen/<citizen_id>', methods=['GET'])
def get_citizen(citizen_id):
    """
    Secured endpoint - requires valid HMAC signature
    """
    # Step 1: Extract required headers
    timestamp = request.headers.get('X-Timestamp')
    nonce = request.headers.get('X-Nonce')
    auth_header = request.headers.get('Authorization')
    
    if not all([timestamp, nonce, auth_header]):
        return jsonify({
            "status": "error",
            "message": "Missing required headers: X-Timestamp, X-Nonce, Authorization"
        }), 400
    
    # Extract signature from Authorization header
    try:
        auth_parts = auth_header.split(' ')
        if len(auth_parts) != 2 or auth_parts[0] != 'HMAC-SHA256':
            return jsonify({
                "status": "error",
                "message": "Invalid Authorization format. Use: HMAC-SHA256 <signature>"
            }), 400
        received_signature = auth_parts[1]
    except:
        return jsonify({"status": "error", "message": "Invalid Authorization header"}), 400
    
    # Step 2: Validate timestamp
    is_valid_ts, ts_message = timestamp_validator.validate(timestamp)
    print(f"   ⏰ Timestamp check: {ts_message}")
    
    if not is_valid_ts:
        return jsonify({
            "status": "error",
            "message": "Request rejected - timestamp validation failed",
            "detail": ts_message
        }), 401
    
    # Step 3: Check nonce uniqueness
    is_unique_nonce, nonce_message = nonce_manager.is_unique(nonce)
    print(f"   🔒 Nonce check: {nonce_message}")
    
    if not is_unique_nonce:
        return jsonify({
            "status": "error",
            "message": "Request rejected - replay attack detected",
            "detail": nonce_message
        }), 401
    
    # Step 4: Create canonical string and verify HMAC
    # For GET requests, body is empty string
    canonical_string = create_canonical_string(
        method="GET",
        path=f"/api/citizen/{citizen_id}",
        body="",  # GET requests have no body
        timestamp=timestamp,
        nonce=nonce
    )
    
    # For demo, we assume client is "irembo-portal"
    # In production, you'd identify client from API key or certificate
    client_id = "irembo-portal"
    
    is_valid_hmac, hmac_message = hmac_verifier.verify(
        client_id=client_id,
        canonical_string=canonical_string,
        received_signature=received_signature
    )
    print(f"   🔐 HMAC check: {hmac_message}")
    
    if not is_valid_hmac:
        return jsonify({
            "status": "error",
            "message": "Request rejected - invalid signature",
            "detail": hmac_message
        }), 401
    
    # Step 5: All checks passed! Process the request
    print(f"   ✅ ALL CHECKS PASSED - Request authenticated!")
    
    if citizen_id in citizen_database:
        return jsonify({
            "status": "success",
            "data": citizen_database[citizen_id],
            "security": {
                "timestamp_valid": True,
                "nonce_unique": True,
                "hmac_valid": True
            }
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": "Citizen not found"
        }), 404

@app.route('/api/dashboard/stats', methods=['GET'])
def get_stats():
    """Get security statistics from middleware"""
    return jsonify({
        "timestamp_validator": {
            "max_age_seconds": timestamp_validator.max_age_seconds
        },
        "nonce_manager": nonce_manager.get_stats(),
        "total_clients": len(hmac_verifier.client_keys)
    })

@app.route('/api/debug/timestamp', methods=['GET'])
def debug_timestamp():
    """Debug endpoint to check server time"""
    return jsonify(timestamp_validator.get_current_time())

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Irembo Secure API Server Starting...")
    print("📍 Server will run at: http://localhost:5000")
    print("📝 Secured endpoints:")
    print("   - GET /api/citizen/<id> (requires valid HMAC)")
    print("📊 Debug endpoints:")
    print("   - GET /api/health")
    print("   - GET /api/dashboard/stats")
    print("   - GET /api/debug/timestamp")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000)