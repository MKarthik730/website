"""
Test script to verify the Storage Web API is working correctly
"""
import requests
import sys

API_URL = "http://localhost:8000/api"

def test_health_check():
    """Test if API is running"""
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed - API is running")
            return True
        else:
            print("❌ Health check failed")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Make sure the backend server is running on port 8000")
        return False

def test_registration():
    """Test user registration"""
    try:
        test_user = {
            "username": "testuser123",
            "email": "test@example.com",
            "password": "testpass123"
        }
        
        response = requests.post(f"{API_URL}/auth/register", json=test_user)
        
        if response.status_code == 200:
            print("✅ User registration works")
            return True
        elif response.status_code == 400 and "already exists" in response.json().get("detail", ""):
            print("✅ User registration works (user already exists)")
            return True
        else:
            print(f"❌ Registration failed: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Registration test error: {e}")
        return False

def test_login():
    """Test user login"""
    try:
        credentials = {
            "username": "testuser123",
            "password": "testpass123"
        }
        
        response = requests.post(f"{API_URL}/auth/login", json=credentials)
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print("✅ User login works - Token received")
                return True, data["access_token"]
            else:
                print("❌ Login succeeded but no token received")
                return False, None
        else:
            print(f"❌ Login failed: {response.json()}")
            return False, None
    except Exception as e:
        print(f"❌ Login test error: {e}")
        return False, None

def test_file_list(token):
    """Test file listing"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/files", headers=headers)
        
        if response.status_code == 200:
            print("✅ File listing works")
            return True
        else:
            print(f"❌ File listing failed: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ File listing test error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Storage Web API Test Suite")
    print("=" * 50)
    print()
    
    tests_passed = 0
    tests_total = 4
    
    # Test 1: Health Check
    if test_health_check():
        tests_passed += 1
    print()
    
    # Test 2: Registration
    if test_registration():
        tests_passed += 1
    print()
    
    # Test 3: Login
    login_success, token = test_login()
    if login_success:
        tests_passed += 1
    print()
    
    # Test 4: File List (requires login)
    if token and test_file_list(token):
        tests_passed += 1
    elif not token:
        print("⚠️  Skipping file list test (no token)")
    print()
    
    # Results
    print("=" * 50)
    print(f"Tests Passed: {tests_passed}/{tests_total}")
    print("=" * 50)
    
    if tests_passed == tests_total:
        print("🎉 All tests passed! The API is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
