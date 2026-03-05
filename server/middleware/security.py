"""
Security Utilities Module
Provides constant-time comparison to prevent timing attacks
"""

import hmac

def constant_time_compare(val1, val2):
    """
    Compare two strings in constant time to prevent timing attacks
    
    Regular comparison (==) stops at the first difference, which leaks
    information about WHERE the strings differ. This function always
    takes the same amount of time regardless of where they differ.
    
    Args:
        val1: First string to compare
        val2: Second string to compare
        
    Returns:
        True if strings are identical, False otherwise
    """
    # Use Python's built-in constant-time comparison
    # This is the same function used by HMAC verification
    return hmac.compare_digest(val1.encode('utf-8') if isinstance(val1, str) else val1,
                               val2.encode('utf-8') if isinstance(val2, str) else val2)

def demonstrate_timing_attack_vulnerability():
    """
    Demo function to show why constant-time comparison is important
    Run this to see the difference!
    """
    import time
    
    secret = "my-secret-key-12345"
    
    print("\n" + "="*60)
    print("🔬 TIMING ATTACK DEMONSTRATION")
    print("="*60)
    
    # Vulnerable comparison (normal ==)
    print("\n❌ VULNERABLE: Regular comparison")
    print("   Stops at first difference - leaks information!")
    
    for guess in ["a", "m", "my-", "my-secret-key-12345"]:
        start = time.time()
        result = (guess == secret)
        duration = (time.time() - start) * 1_000_000  # microseconds
        print(f"   Guess '{guess}': {result} - took {duration:.2f} μs")
    
    # Secure comparison (constant-time)
    print("\n✅ SECURE: Constant-time comparison")
    print("   Always takes same time - no information leakage!")
    
    for guess in ["a", "m", "my-", "my-secret-key-12345"]:
        start = time.time()
        result = constant_time_compare(guess, secret)
        duration = (time.time() - start) * 1_000_000  # microseconds
        print(f"   Guess '{guess}': {result} - took {duration:.2f} μs")
    
    print("\n" + "="*60)

# Run demo if this file is executed directly
if __name__ == "__main__":
    demonstrate_timing_attack_vulnerability()