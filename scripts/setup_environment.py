#!/usr/bin/env python3
import subprocess
import sys
import os
import shutil
from pathlib import Path

script_dir = Path(__file__).parent
base_dir = script_dir.parent
venv_dir = base_dir / '.venv'
frontend_dir = base_dir / 'frontend'
backend_dir = base_dir / 'backend'

# Determine the correct path for the Python executable based on the OS
if os.name == 'nt':  # Windows
    venv_python = venv_dir / 'Scripts' / 'python'
else:  # POSIX (Linux, macOS, etc.)
    venv_python = env_path / 'bin' / 'python'

def setup_backend():
    print("Setting up the backend environment...")
    # Use the system Python to create the virtual environment
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    # Use the Python executable from the virtual environment to install dependencies
    subprocess.run([str(venv_python), "-m", "pip", "install", "-r", str(backend_dir / "requirements.txt")], check=True)

def build_frontend():
    print("Building the frontend...")
    npm_path = shutil.which("npm")
    if not npm_path:
        raise FileNotFoundError("npm command not found. Please ensure Node.js is installed.")
    
    current_dir = os.getcwd()
    os.chdir(frontend_dir)
    subprocess.run([npm_path, "install"], check=True)
    subprocess.run([npm_path, "run", "build"], check=True)
    os.chdir(current_dir)

def main():
    setup_backend()
    build_frontend()
    print("Setup complete.")

if __name__ == "__main__":
    main()
