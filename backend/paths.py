from pathlib import Path

# directories
root_dir = Path(__file__).resolve().parent.parent
data_dir = root_dir / 'data'

# paths
db_path = data_dir / 'paios.db'
