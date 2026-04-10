
import dns.resolver
import requests
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import time
import uuid
import random

# Import Services
from app.services.openrouter_service import OpenRouterReasoner
from app.services.mcp_kali_service import McpKaliService
from app.services.presidio_service import PiiScrubber

router = APIRouter()

# Initialize Services
reasoner = OpenRouterReasoner()
mcp_kali = McpKaliService()
scrubber = PiiScrubber()

from app.services.playwright_service import PlaywrightService
from app.services.pyod_service import AnomalyDetector
from app.services.pinecone_service import VectorDBService
from app.services.rust_binding import RustEngine
from app.services.oast_service import OASTService

# Heavy Duty Services
playwright = PlaywrightService()
anomaly = AnomalyDetector()
pinecone = VectorDBService()
rust = RustEngine()
oast = OASTService()

# --- Security & Verification Models ---

class DomainVerification(BaseModel):
    domain: str
    verification_token: str
    status: str = "pending" # pending, verified
    verified_at: Optional[float] = None

# In-memory storage for prototype (Use DB in production)
VERIFIED_DOMAINS = {
    "secureway.site": {
        "domain": "secureway.site",
        "token": "secureway-verification-demo-token-123",
        "status": "verified",
        "verified_at": time.time()
    },
    "example.com": {
        "domain": "example.com",
        "token": "secureway-verification-demo-token-456",
        "status": "verified",
        "verified_at": time.time()
    }
}  # Format: { "example.com": { ... } }

class VerifyRequest(BaseModel):
    domain: str
    method: str = "file" # 'file' or 'dns'

class ScanRequest(BaseModel):
    url: str

class ScrubRequest(BaseModel):
    text: str

class BolaAnalysisRequest(BaseModel):
    endpoint: str
    user_id: int

class CodeAnalysisRequest(BaseModel):
    code: str
    language: Optional[str] = None
    auto_deploy: bool = False

class PortScanRequest(BaseModel):
    target: str
    fast: bool = True

# --- Verification Logic ---

def normalize_domain(url_or_domain: str) -> str:
    if "://" in url_or_domain:
        from urllib.parse import urlparse
        return urlparse(url_or_domain).hostname or url_or_domain
    return url_or_domain.split("/")[0]

def _check_dns_txt(domain: str, token: str) -> bool:
    try:
        answers = dns.resolver.resolve(domain, 'TXT')
        for rdata in answers:
            if token in str(rdata):
                return True
    except Exception:
        pass # nosec
    return False

def _check_http_file(domain: str, token: str) -> bool:
    try:
        # Check both http and https
        for scheme in ["http", "https"]:
            url = f"{scheme}://{domain}/secureway-verify.txt"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200 and token in resp.text:
                return True
    except Exception:
        pass # nosec
    return False

# --- Endpoints ---

@router.get("/status")
async def system_status():
    return {"system": "SECUREWAY Logic Engine", "status": "operational", "version": "2.1.0 (Secure)"}

@router.post("/assets/register")
async def register_asset(request: VerifyRequest):
    """Register a domain and get a verification token."""
    domain = normalize_domain(request.domain)
    
    # Generate unique token if not exists
    if domain not in VERIFIED_DOMAINS:
        token = f"secureway-verification={str(uuid.uuid4())}"
        VERIFIED_DOMAINS[domain] = {
            "domain": domain,
            "token": token,
            "status": "pending",
            "verified_at": None
        }
    
    return VERIFIED_DOMAINS[domain]

@router.post("/assets/verify")
async def verify_asset(request: VerifyRequest):
    """Verify domain ownership via DNS or File method."""
    domain = normalize_domain(request.domain)
    asset = VERIFIED_DOMAINS.get(domain)
    
    if not asset:
        raise HTTPException(status_code=404, detail="Domain not registered. Register first.")
    
    verified = False
    if request.method == 'dns':
        verified = _check_dns_txt(domain, asset['token'])
    elif request.method == 'file':
        verified = _check_http_file(domain, asset['token'])
    
    if verified:
        asset['status'] = 'verified'
        asset['verified_at'] = time.time()
        return {"success": True, "message": f"Domain {domain} successfully verified.", "asset": asset}
    else:
        raise HTTPException(status_code=400, detail=f"Verification failed. Could not find token '{asset['token']}' using method '{request.method}'.")

@router.get("/assets/list")
async def list_assets():
    return list(VERIFIED_DOMAINS.values())

# --- Protected Scan Endpoints ---

def enforce_ownership(target: str):
    domain = normalize_domain(target)
    asset = VERIFIED_DOMAINS.get(domain)
    if not asset or asset['status'] != 'verified':
        # Bypass for localhost testing if needed, or strictly enforce
        if domain in ["localhost", "127.0.0.1"]:
            return
            
        raise HTTPException(
            status_code=403, 
            detail=f"SECURITY ALERT: Target '{domain}' is NOT verified. You must prove ownership before scanning to prevent misuse."
        )

@router.post("/scan/start")
async def start_scan(request: ScanRequest):
    """Start a security scan - REQUIRES VERIFIED OWNERSHIP"""
    enforce_ownership(request.url)

    scan_id = f"scan_{int(time.time())}" # nosec
    return {
        "scan_id": scan_id,
        "status": "queued",
        "target": request.url,
        "message": "Ownership verified. Scan authorized and starting."
    }

@router.post("/mcp/port_scan")
async def mcp_port_scan(request: PortScanRequest):
    """Run a port scan via Kali MCP - REQUIRES VERIFIED OWNERSHIP"""
    enforce_ownership(request.target)

    result = mcp_kali.port_scan(target=request.target, fast=request.fast)
    
    if not result.get("ok"):
        return {
            "success": False, 
            "message": result.get("message", "MCP Error"),
            "suggestion": "Check Docker/Network"
        }

    data = result.get("data", {})
    return {
        "success": True,
        "target": data.get("target"),
        "output": data.get("output")
    }

# --- Other Logic Endpoints (Mock/Placeholder) ---

@router.get("/scan/{scan_id}/status")
async def scan_status(scan_id: str):
    # Mock status for prototype
    import random
    progress = random.randint(10, 100) # nosec
    threats = []
    
    # Advanced threat simulation using the high-fidelity engine
    
    # 1. Shadow DOM / NetworkX Integration
    if progress > 25:
        shadow_data = await playwright.crawl_shadow_dom(scan_id) # Using scan_id as dummy URL for mock
        threats.append({
            "module": "Headless V8 (Playwright)",
            "severity": "Info",
            "description": f"Mapped {len(shadow_data.get('nodes', []))} shadow nodes. NetworkX graph generated.",
            "nodes": shadow_data.get('nodes', []),
            "coverage": shadow_data.get('coverage')
        })

    # 2. Logic Analysis (BOLA)
    if progress > 50:
        bola_analysis = await reasoner.analyze_bole_flaw("/api/user/data", 101)
        threats.append({
            "module": "Cognitive Context Fuzzing",
            "severity": bola_analysis["severity"],
            "description": bola_analysis["vulnerability"],
            "remediation": bola_analysis["fix_suggestion"]
        })

    # 3. Anomaly Detection (PyOD)
    if progress > 70:
        is_outlier, score = anomaly.detect_outlier([progress, 500]) # Example vector
        if is_outlier:
            threats.append({
                "module": "Traffic Anomaly (PyOD)",
                "severity": "Medium",
                "description": f"Unusual pattern detected in request sequence. Isolation Forest Score: {score:.2f}"
            })

    # 4. Optimized Matching (Rust)
    if progress > 85:
        rust_hash = rust.compute_heavy_hash(b"malicious_string")
        threats.append({
            "module": "Packet Engine (Rust)",
            "severity": "High",
            "description": f"JIT-optimized pattern matching caught suspicious payload signature ({rust_hash[:8]})"
        })

    # 5. OAST (Blind Vulnerabilities)
    if progress > 95:
        oast_res = await oast.check_callbacks()
        if oast_res.get("detected"):
            threats.append({
                "module": "Global OAST Callback Mesh",
                "severity": "Critical",
                "description": f"{oast_res['type']} Interaction detected from {oast_res['source_ip']}"
            })
    
    return {
        "scan_id": scan_id,
        "progress": progress,
        "status": "processing" if progress < 100 else "completed",
        "live_threats": threats
    }

@router.post("/privacy/scrub")
async def scrub_pii(request: ScrubRequest):
    # PII Scrubbing doesn't strictly need domain verification as it's text processing
    text = request.text
    redacted = text.replace("john.doe@example.com", "[REDACTED]")
    return {"original": text, "redacted": redacted}

@router.post("/analyze/bola")
async def analyze_bola(request: BolaAnalysisRequest):
    # BOLA analysis targets an endpoint, so we should verify ownership
    enforce_ownership(request.endpoint)
    result = await reasoner.analyze_bole_flaw(request.endpoint, request.user_id)
    return result

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "api": "operational",
            "scanner": "operational", 
            "scrubber": "operational"
        }
    }
