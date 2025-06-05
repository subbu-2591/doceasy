import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"

def test_doctor_payment_endpoints():
    """Test the new doctor payment history endpoints"""
    
    print("=== Testing Doctor Payment History Endpoints ===")
    
    # First, we need to create some test data
    # Let's test with our existing appointments and payments
    
    # Get doctors first
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
    print(f"✅ Testing with doctor: {doctor['name']} (ID: {doctor_id})")
    
    # Create a mock JWT token for the doctor (in real scenario, this would come from login)
    import jwt
    mock_payload = {
        'id': doctor_id,
        'email': doctor.get('email', 'doctor@example.com'),
        'role': 'doctor',
        'exp': (datetime.utcnow() + timedelta(hours=24)).timestamp()
    }
    
    # Use the same secret key as configured in the app
    mock_token = jwt.encode(mock_payload, 'jwt-secret-key', algorithm='HS256')
    print(f"✅ Generated mock doctor token")
    
    # Test 1: Get doctor payment history
    print(f"\n🔄 Testing payment history endpoint...")
    
    history_response = requests.get(
        f"{BASE_URL}/api/doctor/payments/history",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {mock_token}"
        }
    )
    
    print(f"📊 Payment history status: {history_response.status_code}")
    if history_response.status_code == 200:
        history_data = history_response.json()
        payments = history_data.get('payments', [])
        print(f"✅ Found {len(payments)} payment records")
        
        if payments:
            payment = payments[0]
            print(f"📝 Sample payment: {payment.get('patient_name')} - {payment.get('amount')} INR - {payment.get('payment_status')}")
    else:
        print(f"❌ Payment history failed: {history_response.text}")
    
    # Test 2: Get doctor payment statistics
    print(f"\n🔄 Testing payment statistics endpoint...")
    
    stats_response = requests.get(
        f"{BASE_URL}/api/doctor/payments/stats",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {mock_token}"
        }
    )
    
    print(f"📊 Payment stats status: {stats_response.status_code}")
    if stats_response.status_code == 200:
        stats_data = stats_response.json()
        stats = stats_data.get('stats', {})
        print(f"✅ Payment Statistics:")
        print(f"   💰 Total Earnings: ₹{stats.get('total_earnings', 0)}")
        print(f"   ⏳ On Hold: ₹{stats.get('on_hold_amount', 0)}")
        print(f"   📝 Pending: ₹{stats.get('pending_amount', 0)}")
        print(f"   ✅ Completed: ₹{stats.get('completed_amount', 0)}")
        print(f"   📊 Total Appointments: {stats.get('total_appointments', 0)}")
    else:
        print(f"❌ Payment stats failed: {stats_response.text}")
    
    # Test 3: Test appointment payment details (if we have appointments)
    if history_response.status_code == 200:
        history_data = history_response.json()
        payments = history_data.get('payments', [])
        
        if payments and payments[0].get('appointment_id'):
            appointment_id = payments[0]['appointment_id']
            print(f"\n🔄 Testing appointment payment details for: {appointment_id}")
            
            details_response = requests.get(
                f"{BASE_URL}/api/doctor/payments/appointment/{appointment_id}",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {mock_token}"
                }
            )
            
            print(f"📊 Appointment payment details status: {details_response.status_code}")
            if details_response.status_code == 200:
                details_data = details_response.json()
                payment_details = details_data.get('payment')
                if payment_details:
                    print(f"✅ Payment Details:")
                    print(f"   👤 Patient: {payment_details.get('patient_name')}")
                    print(f"   💰 Amount: ₹{payment_details.get('amount')}")
                    print(f"   📋 Status: {payment_details.get('payment_status')}")
                    print(f"   🆔 Transaction ID: {payment_details.get('transaction_id')}")
                else:
                    print(f"ℹ️ No payment found for this appointment")
            else:
                print(f"❌ Appointment payment details failed: {details_response.text}")
    
    print(f"\n🎉 Doctor Payment History API Test Complete!")

if __name__ == "__main__":
    test_doctor_payment_endpoints() 