"""
Timestamp Validator Module
Checks if the request timestamp is within acceptable time window (5 minutes)
This prevents replay attacks where old requests are resent
"""

import time
from datetime import datetime

class TimestampValidator:
    """Validates that timestamps are fresh (within 5 minutes)"""
    
    def __init__(self, max_age_seconds=300):  # 5 minutes default
        self.max_age_seconds = max_age_seconds
        print("⏰ Timestamp Validator initialized - Max age: 5 minutes")
    
    def validate(self, timestamp_str):
        """
        Validate that the timestamp is within the acceptable window
        
        Args:
            timestamp_str: Unix timestamp as string (e.g., "1678886400")
            
        Returns:
            (is_valid, message) tuple
        """
        try:
            # Convert string to integer (Unix timestamp)
            request_time = int(timestamp_str)
            current_time = int(time.time())
            
            # Calculate age of request
            age = current_time - request_time
            
            # Check if timestamp is in the future (clock skew)
            if age < -60:  # More than 1 minute in the future
                return False, f"❌ Timestamp from the future! Server: {current_time}, Request: {request_time}"
            
            # Check if timestamp is too old
            if age > self.max_age_seconds:
                return False, f"❌ Timestamp expired! Age: {age} seconds, Max allowed: {self.max_age_seconds}"
            
            # All checks passed
            return True, f"✅ Timestamp valid (age: {age} seconds)"
            
        except ValueError:
            return False, f"❌ Invalid timestamp format: {timestamp_str}"
        except Exception as e:
            return False, f"❌ Timestamp validation error: {str(e)}"
    
    def get_current_time(self):
        """Helper to get current server time (for debugging)"""
        return {
            "timestamp": int(time.time()),
            "readable": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }