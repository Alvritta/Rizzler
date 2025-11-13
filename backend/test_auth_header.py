#!/usr/bin/env python3
"""
Test script to verify Authorization header works correctly
"""
import requests
import sys

BASE_URL = "http://localhost:8002"

def test_calculate_rizz(email, password, image_path):
    """Complete test flow: login -> get token -> calculate rizz"""
    
    print("=" * 60)
    print("Testing Rizz Calculator API")
    print("=" * 60)
    
    # Step 1: Login
    print("\n1️⃣ Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login/",
        json={"email": email, "password": password}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    login_data = login_response.json()
    access_token = login_data["access_token"]
    print(f"✅ Login successful!")
    print(f"📝 Access Token: {access_token[:50]}...")
    
    # Step 2: Calculate Rizz with proper Authorization header
    print(f"\n2️⃣ Calculating rizz for {image_path}...")
    
    # Determine content type based on file extension
    import mimetypes
    content_type, _ = mimetypes.guess_type(image_path)
    if not content_type or not content_type.startswith("image/"):
        # Default to jpeg if can't detect
        content_type = "image/jpeg"
    
    print(f"📄 Detected content type: {content_type}")
    
    with open(image_path, "rb") as f:
        # Explicitly set filename and content type
        files = {
            "file": (image_path.split("/")[-1], f, content_type)
        }
        headers = {
            "Authorization": f"Bearer {access_token}"  # ← This is the correct format
        }
        
        print(f"📤 Sending request with header: Authorization: Bearer {access_token[:20]}...")
        
        response = requests.post(
            f"{BASE_URL}/calculate-rizz/",
            headers=headers,
            files=files
        )


    print(f"Response: {response}")
    print(f"\n📥 Response Status: {response.status_code}")
    print(f"📥 Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ SUCCESS! Rizz Score: {result['score']}/100")
        print(f"💡 Suggestions:")
        for i, suggestion in enumerate(result['suggestions'], 1):
            print(f"   {i}. {suggestion}")
        if result.get('reasoning'):
            print(f"\n📝 Reasoning: {result['reasoning']}")
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Debug info
        if "Authorization header missing" in response.text:
            print("\n🔍 DEBUG: Authorization header issue detected!")
            print("Make sure you're sending:")
            print("  Header Name: Authorization")
            print(f"  Header Value: Bearer {access_token[:50]}...")
            print("\nCommon mistakes:")
            print("  ❌ authorization (lowercase)")
            print("  ❌ Authorization: <token> (missing 'Bearer ')")
            print("  ✅ Authorization: Bearer <token>")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python test_auth_header.py <email> <password> <image_path>")
        print("\nExample:")
        print("  python test_auth_header.py test@example.com password123 image.jpg")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    image_path = sys.argv[3]
    
    test_calculate_rizz(email, password, image_path)

