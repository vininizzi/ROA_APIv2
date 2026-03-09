import requests
import json

BASE_URL = "http://localhost:8000"

def test_registration_duplicate():
    payload = {
        "name": "teste",
        "email": "teste@gmail.com",
        "password": "teste1",
        "role": "student"
    }
    
    # First attempt (might already exist, but we want to see the error)
    print(f"Testing registration with: {payload['email']}")
    response = requests.post(f"{BASE_URL}/ROA/register", json=payload)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 400:
        print("SUCCESS: Received 400 Bad Request for duplicate user.")
    elif response.status_code == 200 or response.status_code == 201:
        print("INFO: User created successfully (was not a duplicate). Run again to test duplicate.")
    else:
        print(f"FAILURE: Unexpected status code {response.status_code}")

if __name__ == "__main__":
    try:
        test_registration_duplicate()
    except Exception as e:
        print(f"Error connecting to server: {e}")
