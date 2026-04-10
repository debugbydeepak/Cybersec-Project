
import os
import sys
import subprocess
import glob
from app.services.code_analyzer import CodeAnalyzer
from datetime import datetime

class CIPipeline:
    def __init__(self, root_dir="."):
        self.root_dir = root_dir
        self.analyzer = CodeAnalyzer()
        self.report = []

    def log(self, step, status, message):
        self.report.append(f"[{datetime.now().isoformat()}] [{step}] {status}: {message}")
        print(f"[{step}] {status}: {message}")

    def run_tests(self):
        """Run Pytest suite"""
        self.log("TEST", "STARTING", "Running unit tests...")
        try:
            # Check if tests exist
            if not os.path.exists(os.path.join(self.root_dir, "tests")):
                self.log("TEST", "SKIPPED", "No 'tests' directory found.")
                return True
                
            res = subprocess.run([sys.executable, "-m", "pytest", "tests"], capture_output=True, text=True)
            if res.returncode == 0:
                self.log("TEST", "PASSED", "All tests passed.\n" + res.stdout)
                return True
            else:
                self.log("TEST", "FAILED", "Tests failed.\n" + res.stderr)
                return False
        except Exception as e:
            self.log("TEST", "ERROR", str(e))
            return False

    def run_security_scan(self):
        """Run Bandit (SAST)"""
        self.log("SECURITY", "STARTING", "Running Bandit static analysis...")
        try:
            # Scan app directory recursively
            target = os.path.join(self.root_dir, "app")
            if not os.path.exists(target):
                 self.log("SECURITY", "SKIPPED", "No 'app' directory found.")
                 return True

            res = subprocess.run(["bandit", "-r", target], capture_output=True, text=True)
            if res.returncode == 0: # Bandit exits 0 on no issues or low severity (depending on config)
                 self.log("SECURITY", "PASSED", "No high severity issues found.")
                 return True
            else:
                 # Check if actually 'issues found' or just command error
                 if "No issues identified" in res.stdout:
                      self.log("SECURITY", "PASSED", "Clean scan.")
                      return True
                 self.log("SECURITY", "WARNING", f"Issues found:\n{res.stdout[:500]}...") # truncate
                 return False # For strict pipeline
        except FileNotFoundError:
             self.log("SECURITY", "ERROR", "Bandit not installed.")
             return False

    def run_auto_fix(self):
        """Run internal CodeAnalyzer and generate fixes."""
        self.log("AUTO-FIX", "STARTING", "Analyzing code for auto-fixes...")
        total_fixes = 0
        
        # Walk through python files
        for root, dirs, files in os.walk(os.path.join(self.root_dir, "app")):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    issues = self.analyzer.analyze_file(full_path)
                    
                    if issues:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        original_content = content
                        fixed_content = content
                        
                        for issue in issues:
                            if 'line' in issue: # valid issue
                                self.log("AUTO-FIX", "FOUND", f"{issue['description']} in {file}:{issue['line']}")
                                # Attempt fix
                                fixed_content = self.analyzer.generate_fix(issue, fixed_content)
                        
                        if fixed_content != original_content:
                            with open(full_path, 'w', encoding='utf-8') as f:
                                # f.write(fixed_content) # Safer to not overwrite automatically in a demo without backup
                                pass 
                            self.log("AUTO-FIX", "APPLIED", f"Patched {file} (Simulated write)")
                            total_fixes += 1
        
        if total_fixes == 0:
            self.log("AUTO-FIX", "CLEAN", "No auto-fixable patterns found.")
        return True

    def execute(self):
        steps = [
            self.run_security_scan,
            self.run_tests,
            self.run_auto_fix
        ]
        
        success = True
        for step in steps:
            if not step():
                success = False
                # Continue or break? usually break
                # break 
        
        if success:
             self.log("PIPELINE", "SUCCESS", "Code is safe to push.")
        else:
             self.log("PIPELINE", "FAILURE", "Fix issues before pushing.")
        
        return success

if __name__ == "__main__":
    pipeline = CIPipeline()
    sys.exit(0 if pipeline.execute() else 1)
