import requests
import json
from datetime import datetime, timedelta

# Test the appointment creation endpoint
BASE_URL = "http://localhost:5000"

def test_appointment_creation():
    """Test appointment creation with valid data"""
    
    # First, let's test the health endpoint
    health_response = requests.get(f"{BASE_URL}/api/health-check")
    print(f"Health check status: {health_response.status_code}")
    print(f"Health response: {health_response.json()}")
    
    # Get doctors first to see what's available
    print("\n=== Testing doctors endpoint ===")
    doctors_response = requests.get(f"{BASE_URL}/api/doctors")
    print(f"Doctors endpoint status: {doctors_response.status_code}")
    if doctors_response.status_code == 200:
        doctors = doctors_response.json()
        print(f"Doctors response type: {type(doctors)}")
        if isinstance(doctors, list):
            print(f"Found {len(doctors)} doctors")
            if doctors:
                print(f"First doctor: {doctors[0]}")
                doctor_id = doctors[0].get('id', 'test_doctor')
        else:
            print(f"Doctors response: {doctors}")
            doctor_id = "test_doctor"
    else:
        doctor_id = "test_doctor"
    
    # Try to register a test patient first
    print("\n=== Registering test patient ===")
    patient_data = {
        "firstName": "Test",
        "lastName": "Patient", 
        "email": "testpatient@example.com",
        "password": "testpassword123",
        "gender": "male",
        "dateOfBirth": "1990-01-01",
        "phoneNumber": "+1234567890"
    }
    
    register_response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json=patient_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Register status: {register_response.status_code}")
    print(f"Register response: {register_response.text}")
    
    # Try to login to get a token
    print("\n=== Logging in test patient ===")
    login_data = {
        "email": "testpatient@example.com",
        "password": "testpassword123"
    }
    
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Login status: {login_response.status_code}")
    print(f"Login response: {login_response.text}")
    
    # Test appointment creation without authentication for debugging
    print("\n=== Testing appointment creation with debug bypass ===")
    
    # Test data for appointment creation
    appointment_data = {
        "doctor_id": doctor_id,
        "appointment_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S"),
        "reason": "Test consultation for headache",
        "notes": "Patient has been experiencing headaches for 3 days",
        "consultation_type": "video",
        "urgent": False,
        "preferred_language": "English",
        "medical_history": "No previous medical history",
        "report_complaint": "Headache and fatigue",
        "patient_name": "Test Patient",
        "patient_phone": "+1-555-TEST",
        "patient_email": "testpatient@example.com"
    }
    
    # Try the test create appointment endpoint (no authentication)
    test_create_response = requests.post(
        f"{BASE_URL}/api/test/create-appointment",
        json=appointment_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Test create appointment status: {test_create_response.status_code}")
    print(f"Test create appointment response: {test_create_response.text}")

if __name__ == "__main__":
    test_appointment_creation() 