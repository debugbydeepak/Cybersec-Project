#!/usr/bin/env python3
"""
SECUREWAY Prototype Test Script
Tests all API endpoints to ensure the prototype is working correctly
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(name, method, url, data=None):
    """Test a single API endpoint"""
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{url}")
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{url}", json=data)
        
        status = "✅ PASS" if response.status_code == 200 else "❌ FAIL"
        print(f"{status} {name} - Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2)[:200]}...")
            except:
                print(f"   Response: {response.text[:100]}...")
        else:
            print(f"   Error: {response.text[:100]}...")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ FAIL {name} - Exception: {str(e)}")
        return False

def main():
    print("🔍 SECUREWAY Prototype Test Suite")
    print("=" * 50)
    
    tests = [
        ("Health Check", "GET", "/health"),
        ("Root Status", "GET", "/"),
        ("API Docs", "GET", "/docs"),
        ("Start Scan", "POST", "/scan/start", {"url": "https://example.com"}),
        ("PII Scrubbing", "POST", "/privacy/scrub", {"text": "Contact john.doe@example.com or call 555-1234"}),
        ("BOLA Analysis", "POST", "/analyze/bola", {"endpoint": "/api/orders/123", "user_id": 456}),
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if len(test) == 3:
            name, method, url = test
            data = None
        else:
            name, method, url, data = test
            
        if test_endpoint(name, method, url, data):
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! SECUREWAY prototype is working correctly.")
        print("\n🌐 Access the prototype at:")
        print("   • Backend API: http://localhost:8000/docs")
        print("   • Frontend UI: http://localhost:3000")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
    
    print("\n💡 To use real AI analysis:")
    print("   1. Get a free API key from https://openrouter.ai/")
    print("   2. Copy backend/.env.example to backend/.env")
    print("   3. Add your OpenRouter API key to the .env file")
    print("   4. Restart the backend service")

if __name__ == "__main__":
    main()
