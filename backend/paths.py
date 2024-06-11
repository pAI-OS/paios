from pathlib import Path

# api
api_base_url = '/api/v1'

# paios
base_dir = Path(__file__).resolve().parent.parent
backend_dir = base_dir / 'backend'
frontend_dir = base_dir / 'frontend'
env_file = backend_dir / '.env'

# python venv
venv_dir = base_dir / '.venv'
venv_bin_dir = venv_dir / 'bin'

# data
data_dir = base_dir / 'data'
log_path = data_dir / 'log'
log_db_path = 'file:log?mode=memory&cache=shared'

# abilities
abilities_subdir = 'abilities'
abilities_dir = base_dir / abilities_subdir
abilities_data_dir = data_dir / abilities_subdir

# paths
db_path = data_dir / 'paios.db'
downloads_dir = data_dir / 'downloads'
