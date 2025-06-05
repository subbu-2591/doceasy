import requests
import json

BASE_URL = "http://localhost:5000"

def test_payment_history_simple():
    """Simple test for payment history using test endpoints"""
    
    print("=== Simple Payment History Test ===")
    
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
    
    # Test the payment history endpoint
    print(f"\n🔄 Testing payment history endpoint...")
    
    history_response = requests.get(f"{BASE_URL}/api/test/doctor/payments/history/{doctor_id}")
    print(f"📊 Payment history status: {history_response.status_code}")
    
    if history_response.status_code == 200:
        history_data = history_response.json()
        payments = history_data.get('payments', [])
        print(f"✅ Found {len(payments)} payment records")
        
        if payments:
            print(f"\n💳 Payment Records:")
            for i, payment in enumerate(payments[:3]):  # Show first 3 payments
                print(f"   {i+1}. Patient: {payment.get('patient_name', 'Unknown')}")
                print(f"      Amount: ₹{payment.get('amount', 0)}")
                print(f"      Status: {payment.get('payment_status', 'Unknown')}")
                print(f"      Date: {payment.get('created_at', 'Unknown')}")
                if payment.get('appointment_details'):
                    apt_details = payment['appointment_details']
                    print(f"      Appointment: {apt_details.get('reason', 'Consultation')} on {apt_details.get('appointment_date', 'Unknown')}")
                print()
        
        # Calculate statistics
        total_amount = sum(payment.get('amount', 0) for payment in payments)
        completed_payments = [p for p in payments if p.get('payment_status') == 'completed']
        hold_payments = [p for p in payments if p.get('payment_status') == 'hold']
        pending_payments = [p for p in payments if p.get('payment_status') == 'pending']
        
        print(f"📊 Payment Statistics:")
        print(f"   💰 Total Amount: ₹{total_amount}")
        print(f"   ✅ Completed: {len(completed_payments)} payments (₹{sum(p.get('amount', 0) for p in completed_payments)})")
        print(f"   ⏳ On Hold: {len(hold_payments)} payments (₹{sum(p.get('amount', 0) for p in hold_payments)})")
        print(f"   📝 Pending: {len(pending_payments)} payments (₹{sum(p.get('amount', 0) for p in pending_payments)})")
        
    else:
        print(f"❌ Payment history failed: {history_response.text}")
    
    print(f"\n🎉 Payment History Test Complete!")

if __name__ == "__main__":
    test_payment_history_simple() 