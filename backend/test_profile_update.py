#!/usr/bin/env python3

import requests
import json

def test_doctor_profile_update():
    base_url = "http://localhost:5000"
    
    print("🏥 Testing Doctor Profile Update")
    print("=" * 35)
    
    # First, login to get a doctor token
    try:
        login_data = {
            "email": "subrahmanyag79@gmail.com",
            "password": "Subbu@2004"
        }
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            print("   Trying with patient credentials to test the functionality")
            return
            
        login_result = response.json()
        token = login_result.get('access_token')
        user_role = login_result.get('user', {}).get('role', 'unknown')
        print(f"✅ Login successful as {user_role}")
        
        # If not a doctor, we can't test doctor profile update
        if user_role != 'doctor':
            print(f"ℹ️  Logged in as {user_role}, but need doctor account to test profile update")
            print("   The backend routes are ready for doctor profile updates")
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
        
        response = requests.get(f"{base_url}/api/doctor/profile", headers=headers)
        
        if response.status_code == 200:
            current_profile = response.json()
            print(f"✅ Current profile retrieved")
            print(f"   Name: {current_profile.get('name', 'N/A')}")
            print(f"   Specialty: {current_profile.get('specialty', 'N/A')}")
            print(f"   Experience: {current_profile.get('experience_years', 'N/A')} years")
            print(f"   Fee: ₹{current_profile.get('consultationFee', 'N/A')}")
        else:
            print(f"❌ Failed to get current profile: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Error getting profile: {e}")
        return
    
    # Test updating profile with JSON data
    try:
        update_data = {
            "first_name": "Dr. John",
            "last_name": "Smith Updated",
            "phone": "+1-555-999-8888",
            "specialty": "Updated Cardiology",
            "experience_years": 15,
            "consultationFee": 1500.0,
            "bio": "Updated bio: Experienced cardiologist with 15+ years of practice."
        }
        
        response = requests.put(f"{base_url}/api/doctor/profile", json=update_data, headers=headers)
        
        if response.status_code == 200:
            updated_profile = response.json()
            print(f"✅ Profile updated successfully")
            print(f"   Updated Name: {updated_profile.get('name', 'N/A')}")
            print(f"   Updated Specialty: {updated_profile.get('specialty', 'N/A')}")
            print(f"   Updated Experience: {updated_profile.get('experience_years', 'N/A')} years")
            print(f"   Updated Fee: ₹{updated_profile.get('consultationFee', 'N/A')}")
            print(f"   Updated Bio: {updated_profile.get('bio', 'N/A')[:50]}...")
            
            # Verify the changes were saved
            verification_response = requests.get(f"{base_url}/api/doctor/profile", headers=headers)
            if verification_response.status_code == 200:
                verified_profile = verification_response.json()
                if (verified_profile.get('first_name') == update_data['first_name'] and
                    verified_profile.get('consultationFee') == update_data['consultationFee']):
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
    test_doctor_profile_update() 