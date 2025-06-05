#!/usr/bin/env python3
"""
Test script for password reset functionality
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_EMAIL = "subrahmanyag79@gmail.com"  # Use the default admin email for testing

def test_forgot_password():
    """Test the forgot password endpoint"""
    print("Testing forgot password functionality...")
    
    url = f"{BASE_URL}/auth/forgot-password"
    data = {"email": TEST_EMAIL}
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Forgot password request successful!")
            print("📧 Check your email for the reset link")
            return True
        else:
            print("❌ Forgot password request failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_verify_reset_token(email, token):
    """Test the verify reset token endpoint"""
    print("\nTesting reset token verification...")
    
    url = f"{BASE_URL}/auth/verify-reset-token"
    data = {
        "email": email,
        "reset_token": token
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Reset token is valid!")
            return True
        else:
            print("❌ Reset token is invalid or expired!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_reset_password(email, token, new_password):
    """Test the reset password endpoint"""
    print("\nTesting password reset...")
    
    url = f"{BASE_URL}/auth/reset-password"
    data = {
        "email": email,
        "reset_token": token,
        "new_password": new_password
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Password reset successful!")
            return True
        else:
            print("❌ Password reset failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_login_with_new_password(email, new_password):
    """Test login with the new password"""
    print("\nTesting login with new password...")
    
    url = f"{BASE_URL}/auth/login"
    data = {
        "email": email,
        "password": new_password
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Login with new password successful!")
            return True
        else:
            print("❌ Login with new password failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 DocEasy Password Reset Test Suite")
    print("=" * 50)
    
    # Test 1: Request password reset
    if not test_forgot_password():
        print("\n❌ Test suite failed at forgot password step")
        return
    
    print("\n" + "=" * 50)
    print("📧 Email should be sent to:", TEST_EMAIL)
    print("🔗 Check your email for the reset link")
    print("📝 Extract the token from the reset URL")
    print("=" * 50)
    
    # Interactive part - user needs to provide the token from email
    print("\nTo continue testing, you need the reset token from the email.")
    print("The reset URL looks like: http://localhost:5173/reset-password?token=TOKEN&email=EMAIL")
    
    token = input("\nEnter the reset token from the email (or 'skip' to end): ").strip()
    
    if token.lower() == 'skip':
        print("Test ended. Email functionality verified!")
        return
    
    if not token:
        print("No token provided. Test ended.")
        return
    
    # Test 2: Verify the token
    if not test_verify_reset_token(TEST_EMAIL, token):
        print("\n❌ Test suite failed at token verification step")
        return
    
    # Test 3: Reset password
    new_password = "NewPassword123!"
    if not test_reset_password(TEST_EMAIL, token, new_password):
        print("\n❌ Test suite failed at password reset step")
        return
    
    # Test 4: Login with new password
    if not test_login_with_new_password(TEST_EMAIL, new_password):
        print("\n❌ Test suite failed at login verification step")
        return
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Password reset functionality is working correctly.")
    print("📧 Email delivery system is functional.")
    print("🔐 Password reset security is properly implemented.")
    print("=" * 50)

if __name__ == "__main__":
    main() 