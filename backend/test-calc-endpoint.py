#!/usr/bin/env python3
"""
Test script for Rizz Calculator API with Gemini OCR integration.
Tests full flow: login -> calculate-rizz (image upload + OCR + analysis).
"""
import requests
import sys
import mimetypes
import json

BASE_URL = "http://localhost:8002"  # Update to your deployed URL if needed

def test_rizz_flow(email, password, image_path):
    """Complete test: login, upload image, print results."""
    
    print("=" * 60)
    print("🧪 Testing Rizz Calculator (Gemini OCR + Analysis)")
    print("=" * 60)
    
    # Step 1: Login
    print("\n1️⃣ Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login/",
        json={"email": email, "password": password}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
        return
    
    try:
        login_data = login_response.json()
        # Fixed: Your API returns direct "access_token", not nested in "session"
        access_token = login_data["access_token"]
        print(f"✅ Login successful!")
        print(f"📝 Token: {access_token[:30]}...")
    except KeyError as e:
        print(f"❌ Response parsing error: Missing key {e}. Raw response: {login_response.text}")
        return
    
    # Step 2: Calculate Rizz
    print(f"\n2️⃣ Uploading & analyzing {image_path}...")
    
    # Guess MIME type
    content_type, _ = mimetypes.guess_type(image_path)
    if not content_type or not content_type.startswith("image/"):
        content_type = "image/jpeg"
    
    print(f"📄 Content type: {content_type}")
    
    with open(image_path, "rb") as f:
        files = {"file": (image_path.split("/")[-1], f, content_type)}
        headers = {"Authorization": f"Bearer {access_token}"}
        
        print(f"📤 Sending with Bearer token...")
        response = requests.post(
            f"{BASE_URL}/calculate-rizz/",
            headers=headers,
            files=files
        )
    
    print(f"\n📥 Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"\n✅ SUCCESS!")
            print(f"🎯 Rizz Score: {result['score']}/100")
            print(f"📝 Reasoning: {result.get('reasoning', 'N/A')}")
            print(f"\n💡 Suggestions:")
            for i, suggestion in enumerate(result['suggestions'], 1):
                print(f"   {i}. {suggestion}")
            print(f"\n🖼️  Image URL: {result['image_url']}")
            print(f"🆔 Score ID: {result.get('score_id', 'N/A')}")
        except json.JSONDecodeError:
            print(f"❌ JSON parse error: {response.text}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Auth debug
        if "401" in str(response.status_code) or "Not authenticated" in response.text:
            print("\n🔍 DEBUG: Auth issue? Verify token in headers: 'Bearer <token>'")
        # Upload debug
        if "400" in str(response.status_code) and ("image" in response.text.lower() or "file" in response.text.lower()):
            print("\n🔍 DEBUG: File issue? Check image format/size (<5MB, JPEG/PNG).")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python test-calc-endpoint.py <email> <password> <image_path>")
        print("\nExample:")
        print("  python test-calc-endpoint.py rahuldevbablu@gmail.com 123456 ../tests/test1.jpeg")
        sys.exit(1)
    
    email, password, image_path = sys.argv[1:4]
    test_rizz_flow(email, password, image_path)