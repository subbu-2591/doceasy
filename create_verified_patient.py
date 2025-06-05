import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"

def create_verified_patient():
    """Create a verified patient for testing"""
    
    # Step 1: Register patient
    patient_data = {
        "firstName": "Test",
        "lastName": "Patient", 
        "email": "verified.patient@example.com",
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
    
    if register_response.status_code == 201:
        response_data = register_response.json()
        user_id = response_data.get('user_id')
        dev_otp = response_data.get('dev_otp')
        
        if dev_otp:
            print(f"\nFound dev OTP: {dev_otp}")
            
            # Step 2: Verify OTP
            verify_data = {
                "user_id": user_id,
                "otp": dev_otp
            }
            
            verify_response = requests.post(
                f"{BASE_URL}/api/auth/verify-otp",
                json=verify_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Verify status: {verify_response.status_code}")
            print(f"Verify response: {verify_response.text}")
            
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                access_token = verify_data.get('access_token')
                
                print(f"\n✅ Patient verified successfully!")
                print(f"Access token: {access_token[:50]}...")
                
                return access_token
    
    return None

def test_appointment_with_real_token():
    """Test appointment creation with a real token"""
    
    # Create verified patient and get token
    token = create_verified_patient()
    
    if not token:
        print("❌ Failed to create verified patient")
        return
    
    # Get doctor info
    doctors_response = requests.get(f"{BASE_URL}/api/doctors")
    if doctors_response.status_code != 200:
        print("❌ Failed to get doctors")
        return
    
    doctors = doctors_response.json()
    if not doctors:
        print("❌ No doctors available")
        return
    
    doctor = doctors[0]
    doctor_id = doctor['id']
    
    # Test appointment creation
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    appointment_data = {
        "doctor_id": doctor_id,
        "patient_name": "Test Patient",
        "patient_phone": "+1234567890",
        "patient_email": "verified.patient@example.com",
        "doctor_name": doctor['name'],
        "appointment_date": f"{tomorrow}T10:00:00",
        "reason": "Consultation for headache",
        "notes": "Patient experiencing headaches for 3 days",
        "consultation_type": "video",
        "urgent": False,
        "preferred_language": "English",
        "medical_history": "No previous medical history",
        "report_complaint": "Headache and fatigue"
    }
    
    print(f"\n🔄 Testing appointment creation with real token...")
    
    appointment_response = requests.post(
        f"{BASE_URL}/api/appointments",
        json=appointment_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
    )
    
    print(f"Appointment creation status: {appointment_response.status_code}")
    print(f"Appointment creation response: {appointment_response.text}")
    
    if appointment_response.status_code == 201:
        print("✅ Appointment created successfully!")
        appointment = appointment_response.json()['appointment']
        appointment_id = appointment['id']
        
        # Test payment processing
        print(f"\n🔄 Testing payment processing...")
        
        payment_data = {
            "appointment_id": appointment_id,
            "amount": doctor['consultationFee'],
            "currency": "INR",
            "payment_method": "credit",
            "payment_data": {
                "method": "credit",
                "card_last_four": "1234",
                "cardholder_name": "Test Patient"
            }
        }
        
        payment_response = requests.post(
            f"{BASE_URL}/api/payments/process",
            json=payment_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
        )
        
        print(f"Payment processing status: {payment_response.status_code}")
        print(f"Payment processing response: {payment_response.text}")
        
        if payment_response.status_code == 200:
            print("✅ Payment processed successfully!")
            print("✅ Complete CheckoutPage flow working!")
        else:
            print("❌ Payment processing failed")
    else:
        print("❌ Appointment creation failed")

if __name__ == "__main__":
    test_appointment_with_real_token() 