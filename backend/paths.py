from pathlib import Path

# directories
root_dir = Path(__file__).resolve().parent.parent
venv_dir = root_dir / '.venv'
venv_bin_dir = venv_dir / 'bin'
data_dir = root_dir / 'data'
abilities_subdir = 'abilities'
abilities_dir = root_dir / abilities_subdir
abilities_data_dir = data_dir / abilities_subdir

# paths
db_path = data_dir / 'paios.db'
