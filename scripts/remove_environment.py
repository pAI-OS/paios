#!/usr/bin/env python3
import sys
import shutil
from pathlib import Path

# Ensure the parent directory is in sys.path so relative imports work.
base_dir = Path(__file__).parent.parent
if base_dir not in sys.path:
    sys.path.append(str(base_dir))

ignore_errors = True

# Check if the current environment is the one we're about to delete
venv_path = base_dir / '.venv'
if sys.prefix == str(venv_path):
    print("You are currently in the virtual environment that you're trying to delete. Please deactivate it first.")
    sys.exit(1)

# Remove the virtual environment directory and node_modules
shutil.rmtree(venv_path, ignore_errors=ignore_errors)
shutil.rmtree(base_dir / 'frontend' / 'node_modules', ignore_errors=ignore_errors)
