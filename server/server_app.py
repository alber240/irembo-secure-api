"""
Irembo Secure API - Main Server Application
Simplified version without logging
"""

from flask import Flask, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# Simple in-memory database
citizen_database = {
    "12345": {"id": "12345", "name": "Uwase Diane", "sector": "Gasabo", "age": 32},
    "67890": {"id": "67890", "name": "Mugisha Jean", "sector": "Nyarugenge", "age": 28},
    "11121": {"id": "11121", "name": "Mukamana Alice", "sector": "Kicukiro", "age": 45}
}

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "Irembo Secure API is running"
    })

@app.route('/api/citizen/<citizen_id>', methods=['GET'])
def get_citizen(citizen_id):
    print(f"📥 Request received for citizen ID: {citizen_id}")
    
    if citizen_id in citizen_database:
        return jsonify({
            "status": "success",
            "data": citizen_database[citizen_id]
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": "Citizen not found"
        }), 404

@app.route('/api/dashboard/stats', methods=['GET'])
def get_stats():
    """Simple stats for dashboard"""
    return jsonify({
        "total_requests": 0,
        "accepted": 0,
        "rejected": 0,
        "attack_attempts": 0
    })

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Irembo Secure API Server Starting...")
    print("📍 Server will run at: http://localhost:5000")
    print("📝 API endpoints:")
    print("   - GET /api/health")
    print("   - GET /api/citizen/<id>")
    print("   - GET /api/dashboard/stats")
    print("=" * 50)
    app.run(debug=True, port=5000)