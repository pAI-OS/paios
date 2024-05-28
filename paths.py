from pathlib import Path

# TODO: Implement multi-tenancy e.g.:
#self.backend_path = Path(__file__).resolve().parent
#self.base_path = self.backend_path.parent
#self.db_path = self.base_path / 'data' / (self.tenant if self.tenant else '')
#self.db_path = self.db_path / 'paios.db'

# directories
base_dir = Path(__file__).resolve().parent
venv_dir = base_dir / '.venv'
venv_bin_dir = venv_dir / 'bin'
data_dir = base_dir / 'data'
abilities_subdir = 'abilities'
abilities_dir = base_dir / abilities_subdir
abilities_data_dir = data_dir / abilities_subdir

# paths
db_path = data_dir / 'paios.db'
