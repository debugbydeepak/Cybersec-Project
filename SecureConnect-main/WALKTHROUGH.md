
# SECUREWAY - Security Platform Walkthrough

## 🚀 Getting Started

### 1. Start the Backend Server
The backend powers the logic engine, authentication, and security scanners.
```bash
cd backend
pip install -r requirements.txt
python main.py
```
> The server will start on `http://localhost:8000`.

### 2. Access the Web Interface
Open your browser and navigate to:
**[http://localhost:3000](http://localhost:3000)**
This serves the professional, luxury-themed Django frontend.

### 3. Access the API Documentation
The security logic engine API can be explored at:
**[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## 🔒 Trust & Safety: Domain Verification
To prevent misuse, **SECUREWAY** requires you to verify ownership of any domain you wish to scan.

### How to Verify a Domain:
1. **Register**: Go to the Dashboard -> **Domain Authorization** card.
2. **Enter Domain**: Type `example.com` and click **Generate Token**.
3. **Proof of Ownership**:
   - **Method A (DNS)**: Add a TXT record with the displayed token.
   - **Method B (File)**: Upload `secureway-verify.txt` to your server root with the token inside.
4. **Verify**: Click **Check Verification**.
5. **Scan**: Once verified, the scanner will unlock for that domain.

---

## 🛠️ Advanced Security Features
We have upgraded the engine with industrial-grade Python libraries:
- **Recon**: `shodan`, `requests-html` for deep asset discovery.
- **Scanning**: `python-nmap`, `scapy` for network mapping.
- **Vulnerability**: `python-owasp-zap-v2.4` for DAST.
- **Static Analysis**: `bandit`, `safety` for code security.

## 🤖 CI/CD Automation
To run the automated security pipeline locally:

```bash
cd backend
python pipeline_runner.py
```
This runs:
1. **Bandit** (SAST Security Scan)
2. **Pytest** (Unit Tests)
3. **Auto-Fix Engine** (Python AST Fixer)

A GitHub Actions workflow is also included in `.github/workflows/secureway_ci.yml`.

## ⚠️ Notes
- The "Rust Core" is simulated in this version for demonstration.
- The default login credentials (if any) are based on the registration.
- Ensure Docker is running if you want to use the Kali Linux MCP integration.
