try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

import re

try:
    import shodan
    SHODAN_AVAILABLE = True
except ImportError:
    SHODAN_AVAILABLE = False

try:
    import sqlparse
    SQLPARSE_AVAILABLE = True
except ImportError:
    SQLPARSE_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

from urllib.parse import urljoin, urlparse
import logging

# Configure Logging
logger = logging.getLogger("secureway-scanner")

class AdvancedSecurityScanner:
    """
    Advanced Security Scanner utilizing heavy-duty Python libraries.
    """

    def __init__(self):
        self.shodan_api = None # Initialize with API key if available
        if REQUESTS_AVAILABLE:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'SecureWay-Scanner/2.0 (Defense Research)'
            })

    def scan_dns(self, domain):
        """Perform DNS enumeration using dnspython"""
        if not DNS_AVAILABLE:
             return {"error": "dnspython library not installed."}

        results = {}
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA']
        
        for record in record_types:
            try:
                answers = dns.resolver.resolve(domain, record)
                results[record] = [str(r) for r in answers]
            except Exception:
                results[record] = []
        return results

    def scan_headers(self, url):
        """Analyze HTTP security headers"""
        if not REQUESTS_AVAILABLE:
            return {"error": "requests library not installed."}

        try:
            response = self.session.get(url, timeout=5)
            headers = response.headers
            missing = []
            
            security_headers = [
                'Content-Security-Policy',
                'X-Frame-Options',
                'X-XSS-Protection',
                'Strict-Transport-Security',
                'X-Content-Type-Options'
            ]
            
            for header in security_headers:
                if header not in headers:
                    missing.append(header)
            
            return {
                "status_code": response.status_code,
                "server": headers.get('Server', 'Unknown'),
                "missing_headers": missing,
                "score": max(0, 100 - (len(missing) * 15))
            }
        except Exception as e:
            return {"error": str(e)}

    def check_sqli_patterns(self, content):
        """Check for potential SQL Error messages or patterns using regex"""
        suspicious_patterns = [
            r"SQL syntax.*MySQL",
            r"Warning.*mysql_.*", 
            r"valid MySQL result",
            r"MySqlClient\.",
            r"PostgreSQL.*ERROR",
            r"Warning.*pg_.*",
            r"valid PostgreSQL result",
            r"Npgsql\.",
        ]
        
        findings = []
        for pattern in suspicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                findings.append(f"Potential SQL Error Pattern found: {pattern}")
        
        return findings

    def crawl_and_audit(self, url):
        """Simple crawler to find forms and inputs using BeautifulSoup or simplified regex"""
        if not REQUESTS_AVAILABLE:
             return {"error": "requests library not installed."}

        try:
            response = self.session.get(url, timeout=5)
            
            if BS4_AVAILABLE:
                soup = BeautifulSoup(response.text, 'html.parser')
                forms = soup.find_all('form')
                audit_results = {
                    "forms_found": len(forms),
                    "inputs_found": 0,
                    "risks": []
                }
                
                for form in forms:
                    inputs = form.find_all('input')
                    audit_results["inputs_found"] += len(inputs)
                    
                    action = form.get('action')
                    method = form.get('method', 'get').lower()
                    
                    if method == 'get' and any(i.get('type') == 'password' for i in inputs):
                        audit_results["risks"].append(f"Password field in GET form action: {action}")
                    
                    # Check for CSRF token
                    if not any('csrf' in i.get('name', '').lower() for i in inputs):
                         audit_results["risks"].append(f"Possible missing CSRF token in form action: {action}")
            else:
                # Regex Fallback for Form Detection
                forms = re.findall(r'<form', response.text, re.IGNORECASE)
                audit_results = {
                    "forms_found": len(forms),
                    "inputs_found": len(re.findall(r'<input', response.text, re.IGNORECASE)),
                    "risks": ["Regex mode - BeautifulSoup required for deep audit"],
                    "engine": "SecureWay Regex Crawler (Simplified)"
                }

            return audit_results
            
        except Exception as e:
            return {"error": str(e)}

scanner = AdvancedSecurityScanner()
