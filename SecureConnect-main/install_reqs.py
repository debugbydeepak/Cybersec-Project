import subprocess
import sys

def install_requirements(req_file):
    with open(req_file, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        print(f"Installing {line}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", line])
        except subprocess.CalledProcessError:
            print(f"Failed to install {line}")

if __name__ == "__main__":
    install_requirements("requirements.txt")
    install_requirements("backend/requirements.txt")
