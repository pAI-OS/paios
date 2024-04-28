# PAIOS Backend

## Setup

Create a new python virtual environment (venv) in .venv:

    python3 -m venv .venv

Activate the new environment:

    source .venv/bin/activate

Install dependencies into the venv environment:

    pip install -r requirements.txt

Run the backend python/connexion server:

    python3 main.py

Visit the API to verify it's working:

    http://127.0.0.1:3000/users/142

You should see something like:

    {
        "dateOfBirth": "1997-10-31",
        "email": "alice.smith@gmail.com",
        "firstName": "Alice",
        "id": 142,
        "lastName": "Smith",
        "signUpDate": "2019-08-24"
    }
