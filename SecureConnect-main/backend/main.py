
import os
import sys
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
import time
import random

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("secureway-backend")

# Default Configuration
HOST = "0.0.0.0"
PORT = 8000

# --- ALTERNATE MOCK SERVER (Fallback) ---
class MockHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if self.path == "/" or self.path == "/docs":
            response = {
                "system": "SECUREWAY Logic Engine (Fallback Mode)",
                "status": "operational",
                "stack": {"core": "Python HTTP Server", "ai": "Simulated"}
            }
            self.wfile.write(json.dumps(response).encode())
        elif "/scan/" in self.path and "/status" in self.path:
            # Simulate scan progress
            progress = random.randint(10, 100)
            threats = []
            if progress > 30:
                threats.append({"module": "Agentic Discovery", "severity": "Info", "description": "Mapped 15 shadow DOM nodes (Simulated)"})
            if progress > 60:
                threats.append({"module": "Logic Lab", "severity": "Critical", "description": "BOLA Vulnerability detected (Simulated)"})
                
            response = {
                "scan_id": "scan_mock_123",
                "progress": progress,
                "status": "processing" if progress < 100 else "completed",
                "live_threats": threats
            }
            self.wfile.write(json.dumps(response).encode())
            
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if "/scan/start" in self.path:
            response = {
                "scan_id": f"scan_{int(time.time())}",
                "status": "queued",
                "message": "Scan started in Fallback Simulation Mode"
            }
            self.wfile.write(json.dumps(response).encode())
        elif "/privacy/scrub" in self.path:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                text = data.get("log_text", "")
                redacted = text.replace("john.doe@example.com", "[EMAIL_REDACTED]")
                response = {"original": text, "redacted": redacted, "engine": "Fallback Scrubber"}
                self.wfile.write(json.dumps(response).encode())
            except:
                self.wfile.write(b'{"error": "Invalid JSON"}')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

def run_fallback_server():
    logger.warning("Authentication/Dependencies failed. Starting ALTERNATE FALLBACK SERVER...")
    server = HTTPServer((HOST, PORT), MockHandler)
    print(f"[*] Fallback Server running on http://{HOST}:{PORT}")
    server.serve_forever()

def main():
    try:
        # Try importing critical production dependencies
        import uvicorn
        from fastapi import FastAPI
        
        logger.info("Production dependencies found. Starting FastAPI...")
        # Add current directory to path so 'app' module is found
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # Run Uvicorn
        uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
        
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        run_fallback_server()
    except Exception as e:
        logger.error(f"Critical Error: {e}")
        run_fallback_server()

if __name__ == "__main__":
    main()
