#!/usr/bin/env python3

import requests
import json

def test_login():
    base_url = "http://localhost:5000"
    
    print("🔐 Testing Login Endpoint")
    print("=" * 30)
    
    # Test 1: Ping endpoint
    try:
        response = requests.get(f"{base_url}/api/auth/ping")
        print(f"✅ Ping: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Ping Failed: {e}")
        return
    
    # Test 2: Login with invalid credentials
    try:
        login_data = {
            "email": "test@test.com",
            "password": "test"
        }
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"✅ Login (invalid): {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Login Failed: {e}")
    
    # Test 3: Login with valid admin credentials
    try:
        login_data = {
            "email": "subrahmanyag79@gmail.com",
            "password": "Subbu@2004"
        }
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"✅ Login (admin): {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Role: {data.get('user', {}).get('role')}")
            print(f"   Token: {data.get('access_token', '')[:50]}...")
        else:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Admin Login Failed: {e}")

if __name__ == "__main__":
    test_login() 