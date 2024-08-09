# backend package
import os
from common import paths
from backend.db import init_db

# List of directories to ensure exist
required_directories = [
    paths.data_dir
]

# Create directories if they do not exist
for directory in required_directories:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Initialize the database
init_db()
