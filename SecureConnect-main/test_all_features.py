import requests
import time
import json

BACKEND_URL = "http://localhost:8000"

def test_health():
    print("Testing /health...")
    resp = requests.get(f"{BACKEND_URL}/health")
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.json()}")
    assert resp.status_code == 200

def test_scrub():
    print("\nTesting /privacy/scrub...")
    payload = {"text": "My email is john.doe@example.com and phone is 555-0199"}
    resp = requests.post(f"{BACKEND_URL}/privacy/scrub", json=payload)
    print(f"Status: {resp.status_code}")
    print(f"Redacted: {resp.json().get('redacted')}")
    assert "john.doe@example.com" not in resp.json().get('redacted')

def test_port_scan():
    print("\nTesting /mcp/port_scan...")
    payload = {"target": "127.0.0.1", "fast": True}
    resp = requests.post(f"{BACKEND_URL}/mcp/port_scan", json=payload)
    print(f"Status: {resp.status_code}")
    print(f"Output Snippet: {resp.json().get('output', '')[:100]}...")
    assert resp.status_code == 200
    assert resp.json().get('success') is True

def test_bola():
    print("\nTesting /analyze/bola...")
    payload = {"endpoint": "https://example.com/api/v1/user/101", "user_id": 202}
    resp = requests.post(f"{BACKEND_URL}/analyze/bola", json=payload)
    print(f"Status: {resp.status_code}")
    print(f"Vulnerable: {resp.json().get('vulnerable')}")
    print(f"Explanation: {resp.json().get('explanation')[:100]}...")
    assert resp.status_code == 200

if __name__ == "__main__":
    try:
        test_health()
        test_scrub()
        test_port_scan()
        test_bola()
        print("\n✅ ALL BACKEND FEATURES VERIFIED SUCCESSFULLY!")
    except Exception as e:
        print(f"\n❌ VERIFICATION FAILED: {str(e)}")
        print("Make sure the backend is running (run_secureway.bat)")
