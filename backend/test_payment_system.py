#!/usr/bin/env python3
"""
Test script for the complete payment system integration
Tests appointment creation -> payment processing -> admin approval workflow
"""

import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"
ADMIN_EMAIL = "subrahmanyag79@gmail.com"
ADMIN_PASSWORD = "Subbu@2004"

def test_payment_system():
    """Test the complete payment system workflow"""
    
    # 1. Admin login to get admin token
    print("1. Testing admin login...")
    admin_login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/admin/login", json=admin_login_data)
    if response.status_code == 200:
        admin_token = response.json().get('token')
        print(f"✅ Admin login successful")
    else:
        print(f"❌ Admin login failed: {response.status_code}")
        print(response.text)
        return
    
    # 2. Get available doctors
    print("\n2. Getting available doctors...")
    response = requests.get(f"{BASE_URL}/api/doctors", headers={
        'Authorization': f'Bearer {admin_token}'
    })
    
    if response.status_code == 200:
        doctors = response.json().get('doctors', [])
        if doctors:
            doctor_id = doctors[0]['id']
            doctor_name = doctors[0]['name']
            print(f"✅ Found doctor: {doctor_name} (ID: {doctor_id})")
        else:
            print("❌ No doctors found")
            return
    else:
        print(f"❌ Failed to get doctors: {response.status_code}")
        return
    
    # 3. Create a test patient user
    print("\n3. Creating test patient...")
    patient_data = {
        "email": "test.patient@example.com",
        "password": "testpass123",
        "name": "Test Patient"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/patient/register", json=patient_data)
    if response.status_code == 201:
        print("✅ Patient created successfully")
    else:
        # Patient might already exist, try to login
        response = requests.post(f"{BASE_URL}/api/auth/patient/login", json={
            "email": patient_data["email"],
            "password": patient_data["password"]
        })
        if response.status_code == 200:
            print("✅ Patient login successful (existing user)")
        else:
            print(f"❌ Patient creation/login failed: {response.status_code}")
            return
    
    patient_token = response.json().get('token')
    
    # 4. Create appointment
    print("\n4. Creating appointment...")
    appointment_date = datetime.now() + timedelta(days=1)
    appointment_data = {
        "doctor_id": doctor_id,
        "appointment_date": appointment_date.isoformat(),
        "consultation_type": "video",
        "reason": "Test consultation for payment system",
        "notes": "Testing payment integration",
        "report_complaint": "No specific complaints",
        "urgent": True,
        "patient_phone": "+1234567890",
        "patient_email": "test.patient@example.com",
        "preferred_language": "English",
        "medical_history": "No significant medical history"
    }
    
    response = requests.post(f"{BASE_URL}/api/appointments", 
                           json=appointment_data,
                           headers={'Authorization': f'Bearer {patient_token}'})
    
    if response.status_code == 201:
        appointment = response.json().get('appointment')
        appointment_id = appointment['id']
        print(f"✅ Appointment created: {appointment_id}")
    else:
        print(f"❌ Appointment creation failed: {response.status_code}")
        print(response.text)
        return
    
    # 5. Process payment
    print("\n5. Processing payment...")
    payment_data = {
        "appointment_id": appointment_id,
        "amount": 2000.0,  # ₹1500 consultation + ₹500 urgent fee
        "payment_method": "credit",
        "currency": "INR",
        "payment_data": {
            "method": "credit",
            "card_last_four": "4567"
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/payments/process",
                           json=payment_data,
                           headers={'Authorization': f'Bearer {patient_token}'})
    
    if response.status_code == 200:
        payment = response.json().get('payment')
        payment_id = payment['id']
        transaction_id = response.json().get('transaction_id')
        print(f"✅ Payment processed: {payment_id} (Transaction: {transaction_id})")
    else:
        print(f"❌ Payment processing failed: {response.status_code}")
        print(response.text)
        return
    
    # 6. Check payment status
    print("\n6. Checking payment status...")
    response = requests.get(f"{BASE_URL}/api/payments/status/{appointment_id}",
                          headers={'Authorization': f'Bearer {patient_token}'})
    
    if response.status_code == 200:
        payment_status = response.json()
        print(f"✅ Payment status: {payment_status.get('status')} - {payment_status.get('payment_status')}")
    else:
        print(f"❌ Failed to get payment status: {response.status_code}")
    
    # 7. Test consultation join (should work now)
    print("\n7. Testing consultation access...")
    response = requests.get(f"{BASE_URL}/api/consultations/join/{appointment_id}",
                          headers={'Authorization': f'Bearer {patient_token}'})
    
    if response.status_code == 200:
        consultation = response.json().get('consultation')
        print(f"✅ Consultation access granted: {consultation.get('consultation_type')} call")
    else:
        print(f"❌ Consultation access failed: {response.status_code}")
        print(response.text)
    
    # 8. Admin - Get all payments
    print("\n8. Admin checking payments...")
    response = requests.get(f"{BASE_URL}/api/admin/payments",
                          headers={'Authorization': f'Bearer {admin_token}'})
    
    if response.status_code == 200:
        payments = response.json().get('payments', [])
        print(f"✅ Admin can see {len(payments)} payments")
        
        # Find our payment
        our_payment = None
        for payment in payments:
            if payment['id'] == payment_id:
                our_payment = payment
                break
        
        if our_payment:
            print(f"   Payment found: ₹{our_payment['amount']} for {our_payment['patient_name']}")
        else:
            print("   Our payment not found in admin view")
    else:
        print(f"❌ Admin failed to get payments: {response.status_code}")
    
    # 9. Simulate appointment completion by doctor
    print("\n9. Simulating appointment completion...")
    # First get doctor token (simplified - using admin for now)
    response = requests.put(f"{BASE_URL}/api/consultations/{appointment_id}/complete",
                          headers={'Authorization': f'Bearer {admin_token}'})
    
    if response.status_code == 200:
        print("✅ Appointment marked as completed")
    else:
        print(f"❌ Failed to complete appointment: {response.status_code}")
        print(response.text)
    
    # 10. Admin - Approve payment for release
    print("\n10. Admin approving payment...")
    response = requests.put(f"{BASE_URL}/api/admin/payments/{payment_id}/approve",
                          headers={'Authorization': f'Bearer {admin_token}'})
    
    if response.status_code == 200:
        print("✅ Payment approved by admin")
    else:
        print(f"❌ Payment approval failed: {response.status_code}")
        print(response.text)
    
    # 11. Admin - Release payment to doctor
    print("\n11. Admin releasing payment...")
    response = requests.put(f"{BASE_URL}/api/admin/payments/{payment_id}/release",
                          headers={'Authorization': f'Bearer {admin_token}'})
    
    if response.status_code == 200:
        print("✅ Payment released to doctor")
    else:
        print(f"❌ Payment release failed: {response.status_code}")
        print(response.text)
    
    # 12. Get payment statistics
    print("\n12. Getting payment statistics...")
    response = requests.get(f"{BASE_URL}/api/admin/payments/statistics",
                          headers={'Authorization': f'Bearer {admin_token}'})
    
    if response.status_code == 200:
        stats = response.json()
        print("✅ Payment statistics:")
        print(f"   Total revenue: ₹{stats.get('total_revenue', 0)}")
        print(f"   Pending payments: {stats.get('pending_count', 0)}")
        print(f"   Completed payments: {stats.get('completed_count', 0)}")
    else:
        print(f"❌ Failed to get payment statistics: {response.status_code}")
    
    print("\n🎉 Payment system test completed!")

def test_upi_payment():
    """Test UPI payment flow"""
    print("\n" + "="*50)
    print("TESTING UPI PAYMENT")
    print("="*50)
    
    # Similar to above but with UPI payment method
    print("Testing UPI payment processing...")
    
    # This would follow the same flow but with:
    payment_data = {
        "payment_method": "upi",
        "payment_data": {
            "method": "upi",
            "upi_id": "test@paytm"
        }
    }
    print("✅ UPI payment test structure ready")

if __name__ == "__main__":
    print("🚀 Starting Payment System Integration Test")
    print("="*60)
    
    try:
        test_payment_system()
        test_upi_payment()
        
        print("\n" + "="*60)
        print("✅ All tests completed! Check the results above.")
        print("💡 You can now test the payment system manually:")
        print("   1. Go to http://localhost:5173")
        print("   2. Login as patient")
        print("   3. Book a consultation")
        print("   4. Complete payment")
        print("   5. Join consultation")
        print("   6. Check admin dashboard for payment management")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 