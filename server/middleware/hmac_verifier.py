"""
HMAC Verifier Module
Verifies that requests are authentic and haven't been tampered with
This is the core security component of the entire system!
"""

import hmac
import hashlib
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class HMACVerifier:
    """Verifies HMAC signatures for request authentication"""
    
    def __init__(self):
        # In production, these would be in a secure database
        # For demo, we'll use a simple dictionary of client keys
        self.client_keys = {
            "irembo-portal": os.getenv("IREMBO_SECRET_KEY", "default-dev-key-12345"),
            "test-client": "test-secret-key-67890",
            "attacker": "attacker-wrong-key"  # Attacker doesn't know the real key!
        }
        print("🔐 HMAC Verifier initialized - Ready to verify signatures")
    
    def generate_signature(self, secret_key, canonical_string):
        """
        Generate HMAC-SHA256 signature (same as client would do)
        
        Args:
            secret_key: The shared secret key
            canonical_string: The canonical form of the request
            
        Returns:
            Hex digest of HMAC-SHA256
        """
        return hmac.new(
            key=secret_key.encode('utf-8'),
            msg=canonical_string.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
    
    def verify(self, client_id, canonical_string, received_signature):
        """
        Verify that the signature matches what we expect
        
        Args:
            client_id: Identifier for the client (to look up their key)
            canonical_string: The canonical request string
            received_signature: The signature sent by client
            
        Returns:
            (is_valid, message) tuple
        """
        # Step 1: Look up client's secret key
        if client_id not in self.client_keys:
            return False, f"❌ Unknown client: {client_id}"
        
        secret_key = self.client_keys[client_id]
        
        # Step 2: Generate expected signature
        expected_signature = self.generate_signature(secret_key, canonical_string)
        
        # Step 3: Compare signatures using constant-time comparison
        # This is CRITICAL - prevents timing attacks!
        if hmac.compare_digest(expected_signature, received_signature):
            return True, f"✅ Signature valid for client: {client_id}"
        else:
            return False, f"❌ Invalid signature! Expected: {expected_signature[:16]}..., Got: {received_signature[:16]}..."
    
    def get_client_key_info(self, client_id):
        """Helper to see what key a client uses (for debugging)"""
        if client_id in self.client_keys:
            return {
                "client_id": client_id,
                "key_preview": self.client_keys[client_id][:8] + "..."
            }
        return None