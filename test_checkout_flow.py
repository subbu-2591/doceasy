import requests
import json
from datetime import datetime, timedelta

# Test the exact CheckoutPage.tsx flow
BASE_URL = "http://localhost:5000"

def test_checkout_flow():
    """Test the exact flow that CheckoutPage.tsx uses"""
    
    print("=== CheckoutPage.tsx Flow Test ===")
    
    # Step 1: Get available doctors
    print("\n1. Getting approved doctors...")
    doctors_response = requests.get(f"{BASE_URL}/api/doctors")
    print(f"Doctors endpoint status: {doctors_response.status_code}")
    
    if doctors_response.status_code != 200:
        print("Failed to get doctors")
        return
    
    doctors = doctors_response.json()
    if not doctors:
        print("No doctors available")
        return
    
    doctor = doctors[0]
    doctor_id = doctor['id']
    print(f"Using doctor: {doctor['name']} (ID: {doctor_id})")
    
    # Step 2: Get doctor availability for tomorrow
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"\n2. Getting doctor availability for {tomorrow}...")
    
    availability_response = requests.get(f"{BASE_URL}/api/doctors/{doctor_id}/availability/date/{tomorrow}")
    print(f"Availability status: {availability_response.status_code}")
    print(f"Availability response: {availability_response.text}")
    
    # Step 3: Simulate the appointment data that CheckoutPage creates
    appointment_time = f"{tomorrow}T10:00:00"
    
    appointment_data = {
        "doctor_id": doctor_id,
        "patient_name": "Test Patient",
        "patient_phone": "+1234567890",
        "patient_email": "testpatient@example.com",
        "doctor_name": doctor['name'],
        "appointment_date": appointment_time,
        "reason": "Consultation for headache",
        "notes": "Patient experiencing headaches for 3 days",
        "consultation_type": "video",
        "urgent": False,
        "preferred_language": "English",
        "medical_history": "No previous medical history",
        "report_complaint": "Headache and fatigue"
    }
    
    print(f"\n3. Testing appointment creation with data:")
    print(json.dumps(appointment_data, indent=2))
    
    # Step 4: Try to create appointment (this is where CheckoutPage fails)
    print(f"\n4. Creating appointment...")
    
    # Test without authentication first to see the core error
    appointment_response = requests.post(
        f"{BASE_URL}/api/appointments",
        json=appointment_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Appointment creation status: {appointment_response.status_code}")
    print(f"Appointment creation response: {appointment_response.text}")
    
    if appointment_response.status_code == 401:
        print("\nExpected 401 - authentication required. Let's test with a mock token...")
        
        # Create a mock JWT token for testing (this simulates a logged-in patient)
        import jwt
        mock_payload = {
            'id': 'test_patient_id',
            'email': 'testpatient@example.com',
            'role': 'patient',
            'exp': (datetime.utcnow() + timedelta(hours=24)).timestamp()
        }
        
        # Use the same secret key as configured in the app
        mock_token = jwt.encode(mock_payload, 'jwt-secret-key', algorithm='HS256')
        
        print(f"Generated mock token: {mock_token[:50]}...")
        
        # Try again with mock authentication
        authenticated_response = requests.post(
            f"{BASE_URL}/api/appointments",
            json=appointment_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {mock_token}"
            }
        )
        
        print(f"Authenticated appointment creation status: {authenticated_response.status_code}")
        print(f"Authenticated appointment creation response: {authenticated_response.text}")
        
        if authenticated_response.status_code == 201:
            appointment = authenticated_response.json()['appointment']
            appointment_id = appointment['id']
            
            print(f"\n5. Appointment created successfully! ID: {appointment_id}")
            
            # Step 5: Test payment processing (this is the second part of CheckoutPage flow)
            print(f"\n6. Testing payment processing...")
            
            payment_data = {
                "appointment_id": appointment_id,
                "amount": doctor['consultationFee'],
                "currency": "INR",
                "payment_method": "credit",
                "payment_data": {
                    "method": "credit",
                    "card_last_four": "1234",
                    "cardholder_name": "Test Patient",
                    "billing_address": {
                        "address": "123 Test Street",
                        "city": "Test City",
                        "state": "Test State",
                        "zip_code": "12345"
                    }
                }
            }
            
            payment_response = requests.post(
                f"{BASE_URL}/api/payments/process",
                json=payment_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {mock_token}"
                }
            )
            
            print(f"Payment processing status: {payment_response.status_code}")
            print(f"Payment processing response: {payment_response.text}")
        else:
            print(f"Appointment creation failed with status: {authenticated_response.status_code}")
    
    else:
        print(f"Unexpected response from appointment creation: {appointment_response.status_code}")

if __name__ == "__main__":
    test_checkout_flow() 