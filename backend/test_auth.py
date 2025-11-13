#!/usr/bin/env python3
"""
Quick test script to get access token and use it
"""
import requests
import sys

# Configuration
BASE_URL = "http://localhost:8002"
EMAIL = "rahuldevbablu@gmail.com"  # Change this
PASSWORD = "123456"  # Change this

def get_access_token():
    """Login and get access token"""
    print("🔐 Logging in...")
    response = requests.post(
        f"{BASE_URL}/auth/login/",
        json={"email": EMAIL, "password": PASSWORD}
    )
    
    if response.status_code == 200:
        data = response.json()
        access_token = data["access_token"]
        print(f"✅ Login successful!")
        print(f"📝 Access Token: {access_token[:50]}...")
        return access_token
    else:
        print(f"❌ Login failed: {response.text}")
        sys.exit(1)

def calculate_rizz(access_token, image_path):
    """Calculate rizz score using the access token"""
    print(f"\n🔥 Calculating rizz for {image_path}...")
    
    with open(image_path, "rb") as f:
        files = {"file": f}
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = requests.post(
            f"{BASE_URL}/calculate-rizz/",
            headers=headers,
            files=files
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Rizz Score: {result['score']}/100")
        print(f"💡 Suggestions:")
        for i, suggestion in enumerate(result['suggestions'], 1):
            print(f"   {i}. {suggestion}")
        return result
    else:
        print(f"❌ Error: {response.text}")
        return None

if __name__ == "__main__":
    # Step 1: Get access token
    token = get_access_token()
    
    # Step 2: Use token (if image path provided)
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        calculate_rizz(token, image_path)
    else:
        print(f"\n💡 To calculate rizz, run:")
        print(f"   python {sys.argv[0]} /path/to/image.jpg")
        print(f"\n🔑 Your access token for manual use:")
        print(f"   Authorization: Bearer {token}")


