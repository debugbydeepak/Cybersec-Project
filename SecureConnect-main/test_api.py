
import requests

try:
    print("Testing Backend...")
    # Test Root
    res = requests.get("http://localhost:8000/")
    print("Root:", res.status_code)
    
    # Test Privacy Scrubbing
    payload = {"log_text": "Sensitive data for john.doe@example.com"}
    res = requests.post("http://localhost:8000/privacy/scrub", json=payload)
    print("Scrub API:", res.status_code, res.json())
    
    # Test Scan Start
    scan_pl = {"target_url": "http://test.com"}
    res = requests.post("http://localhost:8000/scan/start", json=scan_pl)
    print("Scan Start API:", res.status_code, res.json())
    
    # Test Scan Status (Simulated ID)
    scan_id = res.json().get("scan_id", "scan_123")
    res = requests.get(f"http://localhost:8000/scan/{scan_id}/status")
    print("Scan Status API:", res.status_code, res.json())

except Exception as e:
    print("Error:", e)
