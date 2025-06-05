import requests

BASE_URL = "http://localhost:5000"
DOCTOR_ID = "6839fd60a580d842b1606005"

def setup_availability():
    """Set up availability for the doctor"""
    
    response = requests.post(f"{BASE_URL}/api/test/setup-doctor-availability/{DOCTOR_ID}")
    print(f"Setup availability status: {response.status_code}")
    print(f"Setup availability response: {response.text}")

if __name__ == "__main__":
    setup_availability() 