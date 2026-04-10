
import ast
import os
from typing import List, Dict, Any

class CodeAnalyzer:
    """
    Automated Code Analysis & Auto-Fix Engine.
    Uses AST parsing to detect insecure patterns and suggests/applies fixes.
    """

    PATTERNS = {
        "eval": {
            "description": "Risk of Arbitrary Code Execution via eval()",
            "fix": "Use ast.literal_eval() for safe evaluation.",
            "severity": "High"
        },
        "os.system": {
            "description": "Command Injection Risk via os.system()",
            "fix": "Use subprocess.run() with shell=False.",
            "severity": "High"
        },
        "requests.get(..., verify=False)": {
            "description": "SSL Certificate Verification Disabled",
            "fix": "Remove verify=False or set to True.",
            "severity": "Medium"
        }, 
        "debug=True": {
            "description": "Debug Mode Enabled in Production",
            "fix": "Set debug=False or use environment variable.",
            "severity": "Critical"
        }
    }

    def analyze_file(self, file_path: str) -> List[Dict[str, Any]]:
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Check for function calls
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id == 'eval':
                            issues.append({
                                "file": file_path,
                                "line": node.lineno,
                                "issue": "eval_detected",
                                "description": self.PATTERNS['eval']['description'],
                                "suggestion": self.PATTERNS['eval']['fix']
                            })
                    elif isinstance(node.func, ast.Attribute):
                        # Detect os.system
                        if isinstance(node.func.value, ast.Name) and node.func.value.id == 'os' and node.func.attr == 'system':
                            issues.append({
                                "file": file_path,
                                "line": node.lineno,
                                "issue": "os_system_detected",
                                "description": self.PATTERNS['os.system']['description'],
                                "suggestion": self.PATTERNS['os.system']['fix']
                            })

            if "debug=True" in content or "debug = True" in content:
                 # Be careful not to match the CodeAnalyzer itself
                 if "PATTERNS" not in content:
                     issues.append({
                        "file": file_path,
                        "line": 0, # Global
                        "issue": "debug_mode",
                        "description": self.PATTERNS['debug=True']['description'],
                        "suggestion": self.PATTERNS['debug=True']['fix']
                    })

        except Exception as e:
            return [{"error": str(e)}]
        
        return issues

    def generate_fix(self, issue: Dict[str, Any], content: str) -> str:
        """
        Applies a fix for a given issue.
        Simple string replacement for prototype.
        """
        lines = content.split('\n')
        line_idx = issue['line'] - 1
        
        if issue['issue'] == 'eval_detected':
            lines[line_idx] = lines[line_idx].replace('eval(', 'ast.literal_eval(')
            # Add import ast if missing (simplistic logic)
            if 'import ast' not in content:
                lines.insert(0, 'import ast')
        
        elif issue['issue'] == 'os_system_detected':
             # This is complex to fix automatically perfectly, but we can suggest
             lines[line_idx] = f"# AUTO-FIX: Replaced os.system\n# {lines[line_idx].replace('os.system', 'subprocess.run')}"
             if 'import subprocess' not in content:
                 lines.insert(0, 'import subprocess')

        elif issue['issue'] == 'debug_mode':
             content = content.replace('debug=True', 'debug=False')
             content = content.replace('debug = True', 'debug = False')
             return content

        return '\n'.join(lines)
