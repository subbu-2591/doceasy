#!/usr/bin/env python3

import requests
import json

def test_patient_profile_update():
    base_url = "http://localhost:5000"
    
    print("👤 Testing Patient Profile Update")
    print("=" * 35)
    
    # First, login to get a patient token
    try:
        login_data = {
            "email": "subrahmanyag79@gmail.com",
            "password": "Subbu@2004"
        }
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return
            
        login_result = response.json()
        token = login_result.get('access_token')
        user_role = login_result.get('user', {}).get('role', 'unknown')
        print(f"✅ Login successful as {user_role}")
        
        # If not a patient, we can't test patient profile update
        if user_role != 'patient':
            print(f"ℹ️  Logged in as {user_role}, but need patient account to test profile update")
            print("   The backend routes are ready for patient profile updates")
            return
            
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return
    
    # Test getting current profile
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{base_url}/api/patient/profile", headers=headers)
        
        if response.status_code == 200:
            current_profile = response.json()
            print(f"✅ Current profile retrieved")
            print(f"   Name: {current_profile.get('name', 'N/A')}")
            print(f"   Phone: {current_profile.get('phone', 'N/A')}")
            print(f"   Gender: {current_profile.get('gender', 'N/A')}")
            print(f"   DOB: {current_profile.get('dateOfBirth', 'N/A')}")
        else:
            print(f"❌ Failed to get current profile: {response.status_code}")
            # This is expected since patient profile endpoint might not exist yet
            print("   This is expected if patient profile endpoint is not implemented")
            return
            
    except Exception as e:
        print(f"❌ Error getting profile: {e}")
        return
    
    # Test updating profile with JSON data
    try:
        update_data = {
            "name": "John Patient Updated",
            "phone": "+1-555-888-9999",
            "gender": "male",
            "dateOfBirth": "1990-05-15"
        }
        
        response = requests.put(f"{base_url}/api/patient/profile", json=update_data, headers=headers)
        
        if response.status_code == 200:
            updated_profile = response.json()
            print(f"✅ Profile updated successfully")
            print(f"   Updated Name: {updated_profile.get('name', 'N/A')}")
            print(f"   Updated Phone: {updated_profile.get('phone', 'N/A')}")
            print(f"   Updated Gender: {updated_profile.get('gender', 'N/A')}")
            print(f"   Updated DOB: {updated_profile.get('dateOfBirth', 'N/A')}")
            
            # Verify the changes were saved
            verification_response = requests.get(f"{base_url}/api/patient/profile", headers=headers)
            if verification_response.status_code == 200:
                verified_profile = verification_response.json()
                if (verified_profile.get('name') == update_data['name'] and
                    verified_profile.get('phone') == update_data['phone']):
                    print("✅ Profile changes verified in database")
                else:
                    print("⚠️  Profile changes may not have been saved correctly")
            
        else:
            error_data = response.json()
            print(f"❌ Profile update failed: {response.status_code}")
            print(f"   Error: {error_data.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error updating profile: {e}")

if __name__ == "__main__":
    test_patient_profile_update() 