#!/usr/bin/env python3
"""
Test script for DocEasy backend API
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{API_URL}/health-check", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_auth_endpoints():
    """Test authentication endpoints"""
    print("\nTesting auth endpoints...")
    try:
        # Test ping endpoint
        response = requests.get(f"{API_URL}/auth/ping", timeout=5)
        if response.status_code == 200:
            print("✅ Auth ping endpoint working")
        else:
            print(f"❌ Auth ping failed with status {response.status_code}")
            
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Auth endpoints test failed: {e}")
        return False

def test_admin_login():
    """Test admin login with default credentials"""
    print("\nTesting admin login...")
    try:
        login_data = {
            "email": "subrahmanyag79@gmail.com",
            "password": "Subbu@2004"
        }
        
        response = requests.post(f"{API_URL}/auth/login", json=login_data, timeout=5)
        if response.status_code == 200:
            print("✅ Admin login successful")
            data = response.json()
            print(f"Admin user: {data.get('user', {}).get('name', 'Unknown')}")
            return data.get('token')
        else:
            print(f"❌ Admin login failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Admin login test failed: {e}")
        return None

def test_doctor_registration():
    """Test doctor registration flow"""
    print("\nTesting doctor registration...")
    try:
        # Test doctor registration
        registration_data = {
            "email": "test.doctor@example.com",
            "password": "TestPassword123",
            "role": "doctor"
        }
        
        response = requests.post(f"{API_URL}/auth/register", json=registration_data, timeout=5)
        if response.status_code == 201:
            print("✅ Doctor registration successful")
            data = response.json()
            print(f"User ID: {data.get('user_id')}")
            if data.get('dev_otp'):
                print(f"Development OTP: {data.get('dev_otp')}")
            return data
        else:
            print(f"❌ Doctor registration failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Doctor registration test failed: {e}")
        return None

def main():
    """Run all tests"""
    print("🏥 DocEasy Backend API Tests")
    print("=" * 40)
    
    # Test health check
    if not test_health_check():
        print("\n❌ Backend is not running or not accessible")
        print("Please start the backend server first:")
        print("cd backend && python app.py")
        return
    
    # Test auth endpoints
    test_auth_endpoints()
    
    # Test admin login
    admin_token = test_admin_login()
    if admin_token:
        print(f"Admin token: {admin_token[:20]}...")
    
    # Test doctor registration
    doctor_data = test_doctor_registration()
    
    print("\n" + "=" * 40)
    print("🎉 Backend tests completed!")
    
    if admin_token and doctor_data:
        print("\n✅ All core functionality is working!")
        print("\nNext steps:")
        print("1. Start the frontend: cd frontend && npm run dev")
        print("2. Test doctor registration in the browser")
        print("3. Complete doctor profile setup")
        print("4. Test admin verification workflow")
    else:
        print("\n⚠️  Some tests failed. Please check the backend logs.")

if __name__ == "__main__":
    main() 