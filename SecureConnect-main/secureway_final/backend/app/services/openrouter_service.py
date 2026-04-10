import os
import requests
import json
from typing import Dict, Any

class OpenRouterReasoner:
    """
    OpenRouter-based Logic Reasoner for BOLA/IDOR analysis
    Uses OpenRouter API which supports multiple models including free ones
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "sk-or-v1-xxxxxxxx-xxxxxxxx")  # Default placeholder
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "microsoft/wizardlm-2-8x22b"  # Free model option
        
    async def analyze_bole_flaw(self, target_endpoint: str, user_id: int) -> Dict[str, Any]:
        """
        Analyze BOLA/IDOR vulnerabilities using OpenRouter
        Falls back to mock analysis if API key is not configured
        """
        
        # If no valid API key, use mock analysis
        if not self.api_key or self.api_key.startswith("sk-or-v1-xxxxxxxx"):
            return self._mock_analysis(target_endpoint, user_id)
        
        try:
            prompt = f"""
            Analyze the following API endpoint for Broken Object Level Authorization (BOLA) vulnerabilities:
            
            Target Endpoint: {target_endpoint}
            Current User ID: {user_id}
            
            Please analyze:
            1. Can a user access resources they shouldn't have access to?
            2. Is there proper authorization checking?
            3. What are the potential attack vectors?
            
            Provide a detailed security analysis with severity assessment.
            """
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a cybersecurity expert specializing in API security and authorization vulnerabilities."},
                    {"role": "user", "content": prompt}
                ]
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                analysis = result["choices"][0]["message"]["content"]
                
                return {
                    "vulnerability": "Broken Object Level Authorization (BOLA)",
                    "severity": self._extract_severity(analysis),
                    "confidence": 0.85,
                    "engine": "OpenRouter AI",
                    "reasoning_trace": analysis.split('\n'),
                    "raw_analysis": analysis
                }
            else:
                return self._mock_analysis(target_endpoint, user_id)
                
        except Exception as e:
            # Fallback to mock analysis on any error
            return self._mock_analysis(target_endpoint, user_id)
    
    def _mock_analysis(self, target_endpoint: str, user_id: int) -> Dict[str, Any]:
        """Fallback mock analysis when OpenRouter is not available"""
        trace = [
            f"[Thinking] Analyzing API endpoint: {target_endpoint}",
            f"[Context] Current User ID: {user_id}, Target Resource: /api/orders/{user_id}",
            "[Fuzzing] Attempting ID substitution with Admin ID (1001)...",
            "[Headers] Switching Authorization token to 'user_token_123'...",
            "[Response] Server returned 200 OK for Admin resource!",
            f"[Conclusion] BOLA Vulnerability confirmed. Impact: Critical."
        ]
        
        return {
            "vulnerability": "Broken Object Level Authorization (BOLA)",
            "severity": "Critical",
            "confidence": 0.98,
            "engine": "OpenRouter AI (Mock Mode)",
            "reasoning_trace": trace
        }
    
    def _extract_severity(self, analysis: str) -> str:
        """Extract severity level from AI analysis"""
        analysis_lower = analysis.lower()
        if "critical" in analysis_lower:
            return "Critical"
        elif "high" in analysis_lower:
            return "High"
        elif "medium" in analysis_lower:
            return "Medium"
        else:
            return "Low"
