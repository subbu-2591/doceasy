#!/usr/bin/env python3

import requests
import json

def test_backend():
    base_url = "http://localhost:5000"
    
    print("🏥 Testing DocEasy Backend Connection")
    print("=" * 50)
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health Check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return
    
    # Test 2: Admin login
    try:
        login_data = {
            "email": "subrahmanyag79@gmail.com",
            "password": "Subbu@2004"
        }
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"✅ Admin Login: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            user_role = data.get('user', {}).get('role')
            print(f"   Role: {user_role}")
            print(f"   Token: {token[:50]}..." if token else "   No token received")
            
            if token and user_role == 'admin':
                # Test 3: Admin API calls
                headers = {'Authorization': f'Bearer {token}'}
                
                # Test doctors endpoint
                try:
                    response = requests.get(f"{base_url}/api/admin/doctors", headers=headers)
                    print(f"✅ Admin Doctors API: {response.status_code}")
                    if response.status_code == 200:
                        doctors = response.json()
                        print(f"   Found {len(doctors)} doctors")
                except Exception as e:
                    print(f"❌ Admin Doctors API Failed: {e}")
                
                # Test patients endpoint
                try:
                    response = requests.get(f"{base_url}/api/admin/patients", headers=headers)
                    print(f"✅ Admin Patients API: {response.status_code}")
                    if response.status_code == 200:
                        patients = response.json()
                        print(f"   Found {len(patients)} patients")
                except Exception as e:
                    print(f"❌ Admin Patients API Failed: {e}")
                
                # Test dashboard stats
                try:
                    response = requests.get(f"{base_url}/api/admin/dashboard/stats", headers=headers)
                    print(f"✅ Admin Dashboard Stats: {response.status_code}")
                    if response.status_code == 200:
                        stats = response.json()
                        print(f"   Stats: {json.dumps(stats, indent=2)}")
                except Exception as e:
                    print(f"❌ Admin Dashboard Stats Failed: {e}")
                    
                # Test notifications
                try:
                    response = requests.get(f"{base_url}/api/admin/notifications", headers=headers)
                    print(f"✅ Admin Notifications API: {response.status_code}")
                    if response.status_code == 200:
                        notifications = response.json()
                        print(f"   Found {len(notifications)} notifications")
                except Exception as e:
                    print(f"❌ Admin Notifications API Failed: {e}")
            else:
                print("❌ Invalid login response or not admin role")
        else:
            print(f"❌ Login failed: {response.json()}")
    except Exception as e:
        print(f"❌ Admin Login Failed: {e}")

if __name__ == "__main__":
    test_backend() 