from pathlib import Path

# api
api_base_url = '/api/v1'

# paios
base_dir = Path(__file__).resolve().parent.parent
common_dir = base_dir / 'common'
backend_dir = base_dir / 'backend'
frontend_dir = base_dir / 'frontend'
env_file = backend_dir / '.env'

# python venv
venv_dir = base_dir / '.venv'
venv_bin_dir = venv_dir / 'bin'

# data
data_dir = base_dir / 'data'
cert_dir = data_dir / 'cert'
apps_dir = data_dir / 'apps'
envs_dir = data_dir / 'envs'
log_dir = data_dir / 'log'

# logs
log_db_path = 'file:log?mode=memory&cache=shared'

# abilities
abilities_subdir = 'abilities'
abilities_dir = base_dir / abilities_subdir
abilities_data_dir = data_dir / abilities_subdir

# paths
db_name = 'paios.db'
db_path = data_dir / db_name
db_url = f"sqlite+aiosqlite:///{db_path}"
downloads_dir = data_dir / 'downloads'

