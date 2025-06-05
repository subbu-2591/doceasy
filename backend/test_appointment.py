#!/usr/bin/env python3

import requests
import json
from datetime import datetime, timedelta

def test_appointment_creation():
    base_url = "http://localhost:5000"
    
    print("🗓️ Testing Enhanced Appointment Creation")
    print("=" * 45)
    
    # First, login to get a token
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
        print(f"✅ Login successful, token obtained")
        
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return
    
    # Get doctors list to get a valid doctor ID
    try:
        response = requests.get(f"{base_url}/api/doctors")
        if response.status_code == 200:
            doctors = response.json()
            if doctors:
                doctor_id = doctors[0]['id']
                doctor_name = doctors[0].get('name', 'Unknown Doctor')
                print(f"✅ Found doctor: {doctor_name} (ID: {doctor_id})")
            else:
                print("❌ No doctors found")
                return
        else:
            print(f"❌ Failed to get doctors: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error getting doctors: {e}")
        return
    
    # Test enhanced appointment creation
    try:
        # Prepare appointment data with all new fields
        appointment_date = (datetime.now() + timedelta(days=1)).isoformat()
        
        appointment_data = {
            "doctor_id": doctor_id,
            "doctor_name": doctor_name,
            "appointment_date": appointment_date,
            "consultation_type": "video",
            "reason": "Test consultation for enhanced booking",
            "notes": "This is a test appointment with enhanced fields",
            "urgent": True,
            "patient_phone": "+1-555-123-4567",
            "patient_email": "test@example.com",
            "preferred_language": "English",
            "medical_history": "No significant medical history",
            "report_complaint": "No complaints or issues to report"
        }
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(f"{base_url}/api/appointments", json=appointment_data, headers=headers)
        
        if response.status_code == 201:
            result = response.json()
            appointment = result.get('appointment', {})
            
            print(f"✅ Enhanced appointment created successfully!")
            print(f"   Appointment ID: {appointment.get('id')}")
            print(f"   Doctor: {appointment.get('doctor_name')}")
            print(f"   Date: {appointment.get('appointment_date')}")
            print(f"   Type: {appointment.get('consultation_type')}")
            print(f"   Urgent: {appointment.get('urgent')}")
            print(f"   Phone: {appointment.get('patient_phone')}")
            print(f"   Language: {appointment.get('preferred_language')}")
            print(f"   Status: {appointment.get('status')}")
            
            # Verify all fields were saved
            required_fields = ['consultation_type', 'urgent', 'patient_phone', 'preferred_language', 'medical_history']
            missing_fields = [field for field in required_fields if not appointment.get(field)]
            
            if missing_fields:
                print(f"⚠️  Some fields may not have been saved: {missing_fields}")
            else:
                print("✅ All enhanced fields were saved successfully!")
                
        else:
            error_data = response.json()
            print(f"❌ Appointment creation failed: {response.status_code}")
            print(f"   Error: {error_data.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error creating appointment: {e}")

if __name__ == "__main__":
    test_appointment_creation() 