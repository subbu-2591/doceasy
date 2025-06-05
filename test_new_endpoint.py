import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"

def test_new_appointment_endpoint():
    """Test the new comprehensive appointment creation endpoint"""
    
    print("=== Testing New Appointment Creation Endpoint ===")
    
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
    consultation_fee = doctor.get('consultationFee', 500)
    
    print(f"✅ Using doctor: {doctor['name']} (ID: {doctor_id})")
    print(f"✅ Consultation fee: ₹{consultation_fee}")
    
    # Test appointment creation with payment
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    appointment_data = {
        "doctor_id": doctor_id,
        "patient_name": "Test Patient",
        "patient_phone": "+1234567890",
        "patient_email": "testpatient@example.com",
        "doctor_name": doctor['name'],
        "appointment_date": f"{tomorrow}T10:00:00",
        "reason": "Consultation for headache",
        "notes": "Patient experiencing headaches for 3 days",
        "consultation_type": "video",
        "urgent": False,
        "preferred_language": "English",
        "medical_history": "No previous medical history",
        "report_complaint": "Headache and fatigue",
        "amount": consultation_fee,
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
    
    print(f"\n🔄 Testing appointment creation with payment...")
    print(f"📅 Appointment date: {appointment_data['appointment_date']}")
    print(f"💰 Amount: ₹{appointment_data['amount']}")
    
    # Test without authentication (should work with mock user)
    response = requests.post(
        f"{BASE_URL}/api/appointments/create-with-payment",
        json=appointment_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\n📊 Response Status: {response.status_code}")
    print(f"📊 Response: {response.text}")
    
    if response.status_code == 201:
        result = response.json()
        appointment = result.get('appointment', {})
        payment = result.get('payment', {})
        
        print(f"\n✅ SUCCESS! Appointment created successfully!")
        print(f"🆔 Appointment ID: {appointment.get('id')}")
        print(f"📅 Appointment Date: {appointment.get('appointment_date')}")
        print(f"👨‍⚕️ Doctor: {appointment.get('doctor_name')}")
        print(f"👤 Patient: {appointment.get('patient_name')}")
        print(f"📋 Status: {appointment.get('status')}")
        
        if payment:
            print(f"\n💳 Payment Details:")
            print(f"🆔 Payment ID: {payment.get('payment_id')}")
            print(f"🔢 Transaction ID: {payment.get('transaction_id')}")
            print(f"📊 Status: {payment.get('status')}")
            print(f"💰 Amount: ₹{payment.get('amount')}")
        
        print(f"\n🎉 Complete CheckoutPage flow working!")
        
        # Test with authentication token as well
        print(f"\n🔄 Testing with mock authentication token...")
        
        mock_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"  # Mock token
        
        auth_response = requests.post(
            f"{BASE_URL}/api/appointments/create-with-payment",
            json=appointment_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {mock_token}"
            }
        )
        
        print(f"📊 Auth Response Status: {auth_response.status_code}")
        if auth_response.status_code == 201:
            print("✅ Authentication flow also working!")
        else:
            print(f"⚠️ Auth flow response: {auth_response.text}")
        
    else:
        print(f"❌ FAILED! Status: {response.status_code}")
        try:
            error_data = response.json()
            print(f"❌ Error: {error_data.get('error', 'Unknown error')}")
            if 'details' in error_data:
                print(f"❌ Details: {error_data['details']}")
        except:
            print(f"❌ Raw response: {response.text}")

if __name__ == "__main__":
    test_new_appointment_endpoint() 