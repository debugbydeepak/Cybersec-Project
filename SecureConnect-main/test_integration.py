import requests
import sys
import os

# Configuration
DJANGO_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:8000"

def test_backend_health():
    print("Checking FastAPI Backend Health...")
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            print("✅ Backend is Online")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend is Offline: {str(e)}")
        return False

def test_django_health():
    print("Checking Django Frontend Health...")
    try:
        response = requests.get(f"{DJANGO_URL}/")
        if response.status_code == 200:
            print("✅ Django is Online")
            return True
        else:
            # Django might redirect to login, which is fine
            if response.status_code == 302 or "login" in response.url:
                print("✅ Django is Online (Redirected to Login)")
                return True
            print(f"❌ Django returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Django is Offline: {str(e)}")
        return False

def test_pii_scrubbing_integration():
    print("Testing PII Scrubbing Integration...")
    payload = {"log_text": "Internal error at user john.doe@example.com"}
    try:
        response = requests.post(f"{BACKEND_URL}/privacy/scrub", json=payload)
        if response.status_code == 200:
            result = response.json()
            if "[EMAIL_REDACTED]" in result.get("redacted", ""):
                print("✅ PII Scrubbing Integration Works")
                return True
            else:
                print("❌ PII Scrubbing failed to redact email")
                return False
        else:
            print(f"❌ PII Scrubbing API failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ PII Scrubbing Integration Error: {str(e)}")
        return False

def main():
    print("="*50)
    print("SECUREWAY Integration Test Suite")
    print("="*50)
    
    b_health = test_backend_health()
    d_health = test_django_health()
    pii_works = test_pii_scrubbing_integration()
    
    print("="*50)
    if b_health and d_health and pii_works:
        print("🎉 INTEGRATION SUCCESSFUL")
        print("The Django frontend and FastAPI backend are ready for communication.")
    else:
        print("⚠️ INTEGRATION INCOMPLETE")
        print("Please ensure both servers are running using 'run_secureway.bat'")
    print("="*50)

if __name__ == "__main__":
    main()
