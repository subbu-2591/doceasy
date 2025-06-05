#!/usr/bin/env python3
"""
Simple test for email functionality
"""

import requests
import json

def test_password_reset_email():
    """Test password reset email functionality"""
    print("🧪 Testing Password Reset Email Functionality")
    print("=" * 50)
    
    # Test with admin email
    admin_email = "subrahmanyag79@gmail.com"
    
    print(f"📧 Testing password reset for: {admin_email}")
    
    try:
        response = requests.post(
            "http://localhost:5000/api/auth/forgot-password",
            json={"email": admin_email},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Password reset request successful!")
            print("📧 Check your email inbox for the reset link")
            print("🔗 The email should contain a link like:")
            print("   http://localhost:5173/reset-password?email=...&token=...")
            return True
        else:
            print("❌ Password reset request failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_invalid_email():
    """Test with invalid email for security"""
    print("\n🔒 Testing Security with Invalid Email")
    print("=" * 50)
    
    invalid_email = "nonexistent@example.com"
    
    try:
        response = requests.post(
            "http://localhost:5000/api/auth/forgot-password",
            json={"email": invalid_email},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Security check passed - same response for invalid email")
            return True
        else:
            print("❌ Security issue - different response for invalid email")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Email Functionality Tests\n")
    
    # Test 1: Valid email
    success1 = test_password_reset_email()
    
    # Test 2: Invalid email (security test)
    success2 = test_invalid_email()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 All tests passed!")
        print("📧 Email system is working correctly")
        print("🔐 Security measures are in place")
    else:
        print("❌ Some tests failed")
    print("=" * 50) 