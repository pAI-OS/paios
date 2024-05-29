# Personal Artificial Intelligence Operating System (pAI-OS)

## Getting Started

## Notice
|❗ The server binds to localhost without authentication for the time being; this is a security issue that will be fixed before release to end users. You can use any username and password for the time being.|
|--|

### Users

An easy to use release is coming soon, but for now you can follow the instructions below to get started.

### Early Adopters

Clone only the canary branch from the repository:

```sh
git clone --branch canary --single-branch https://github.com/pAI-OS/paios.git
```

Setup the environment:

POSIX (Linux/macOS/etc.):

```sh
python3 paios/scripts/setup_environment.py` (only on first run)
source paios/.venv/bin/activate
python3 -m paios
```

Windows:

```sh
python .\paios\scripts\setup_environment.py (only on first run)
.\paios\.venv\Scripts\Activate.ps1
python -m paios
```

Visit [http://localhost:3080/](http://localhost:3080/)

### Developers

Clone the entire repository:

```sh
git clone https://github.com/Kwaai-AI-Lab/paios.git
```
Build the frontend:

```sh
cd frontend
npm run build
cd ..
```

Run the uvicorn server:

```sh
python -m paios
```

Visit [http://localhost:3080/](http://localhost:3080/)
