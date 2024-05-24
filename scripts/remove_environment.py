#!/usr/bin/env python3
import shutil
from pathlib import Path

# Determine the base directory relative to this script
script_dir = Path(__file__).parent
base_dir = script_dir.parent
ignore_errors = False

# Remove the virtual environment directory and node_modules
shutil.rmtree(base_dir / '.venv', ignore_errors=ignore_errors)
shutil.rmtree(base_dir / 'frontend' / 'node_modules', ignore_errors=ignore_errors)
