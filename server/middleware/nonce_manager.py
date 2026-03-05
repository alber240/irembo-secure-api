"""
Nonce Manager Module
Tracks used nonces to prevent replay attacks
A nonce can only be used once - ever!
"""

import time
from collections import deque
import threading

class NonceManager:
    """Manages used nonces with automatic cleanup of old entries"""
    
    def __init__(self, max_nonces=10000, cleanup_interval=300):
        """
        Initialize nonce manager
        
        Args:
            max_nonces: Maximum number of nonces to store
            cleanup_interval: Remove nonces older than this (seconds)
        """
        self.used_nonces = {}  # Dictionary: nonce -> timestamp
        self.max_nonces = max_nonces
        self.cleanup_interval = cleanup_interval
        self.lock = threading.Lock()  # For thread safety
        
        print("🔒 Nonce Manager initialized - Max nonces: 10,000")
    
    def is_unique(self, nonce, current_time=None):
        """
        Check if nonce is unique (not used before)
        
        Args:
            nonce: The nonce string to check
            current_time: Current time (for testing, auto-detected if None)
            
        Returns:
            True if nonce is unique, False if it's a replay
        """
        if current_time is None:
            current_time = int(time.time())
        
        with self.lock:
            if nonce in self.used_nonces:
                # This nonce has been used before - REPLAY ATTACK!
                first_used = self.used_nonces[nonce]
                age = current_time - first_used
                return False, f"❌ Replay attack detected! Nonce first used {age} seconds ago"
            
            # New nonce - store it
            self.used_nonces[nonce] = current_time
            
            # Trigger cleanup if needed
            if len(self.used_nonces) > self.max_nonces:
                self._cleanup_old_nonces(current_time)
            
            return True, f"✅ Nonce accepted (total stored: {len(self.used_nonces)})"
    
    def _cleanup_old_nonces(self, current_time):
        """Remove nonces older than cleanup_interval"""
        cutoff = current_time - self.cleanup_interval
        old_count = 0
        
        # Find and remove old nonces
        to_delete = [n for n, ts in self.used_nonces.items() if ts < cutoff]
        for nonce in to_delete:
            del self.used_nonces[nonce]
            old_count += 1
        
        if old_count > 0:
            print(f"🧹 Cleaned up {old_count} old nonces. Total now: {len(self.used_nonces)}")
    
    def get_stats(self):
        """Return statistics about stored nonces"""
        return {
            "total_stored": len(self.used_nonces),
            "oldest": min(self.used_nonces.values()) if self.used_nonces else None,
            "newest": max(self.used_nonces.values()) if self.used_nonces else None
        }