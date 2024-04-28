from flask import jsonify
import os
import json
import os
import db

# List of users
# TODO: We're not implementing multi-user yet so this is subject to change
users = [
    {
        "id": 142,
        "firstName": "Alice",
        "lastName": "Smith",
        "email": "alice.smith@gmail.com",
        "dateOfBirth": "1997-10-31",
        "signUpDate": "2019-08-24"
    },
    {
        "id": 351,
        "firstName": "Bob",
        "lastName": "Jones",
        "email": "bob.jones@gmail.com",
        "dateOfBirth": "1975-11-02",
        "signUpDate": "2022-10-02"
    },
]

# List of abilities
abilities = []

abilities_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "abilities"))
for subdir, dirs, files in os.walk(abilities_dir):
    for file in files:
        if file == "metadata.json":
            metadata_path = os.path.join(subdir, file)
            try:
                with open(metadata_path) as f:
                    metadata = json.load(f)
                    abilities.append(metadata)
            except (FileNotFoundError, json.JSONDecodeError):
                pass

# abilities = [
#     {
#         "id": "optical-character-recognition",
#         "name": "Optical Character Recognition",
#         "description": "Conversion of images to text"
#     },
#     {
#         "id": "vector-database",
#         "name": "Vector Database",
#         "description": "Stores vectors (fixed-length lists of numbers) along with other data items"
#     }
# ]

# List of assets
# TODO: These should be read from storage sources like local directory, S3, NAS, Solid pod, etc.
assets = [
  {
    "id": 523,
    "title": "Attention Is All You Need",
    "userId": 142,
    "creator": "Ashish Vaswani et al",
    "subject": "Artificial Intelligence",
    "description": "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely."
  },
  {
    "id": 952,
    "title": "Generative Adversarial Networks",
    "userId": 351,
    "creator": "Goodfellow et al",
    "subject": "Artificial Intelligence",
    "description": "We propose a new framework for estimating generative models via an adversarial process, in which we simultaneously train two models: a generative model G that captures the data distribution, and a discriminative model D that estimates the probability that a sample came from the training data rather than G."
  }
]


def retrieve_all(payload, status_code=200):
        #response = make_response(jsonify(payload), status_code) # Return the user objects and a 200 OK status code
        #response.headers['X-Total-Count'] = len(payload)
        #return response
        return jsonify(payload), status_code, {'X-Total-Count': len(payload)}

def retrieve_user_by_id(userId):

    for user in users:
        if user['id'] == userId:
            return user, 200  # Return the user object and a 200 OK status code
        
    return {"error": "User not found"}, 404  # Return an error message and a 404 Not Found status code


def not_implemented():
    return {"message": "This operation is not implemented yet."}, 501


def update_user_by_id(userId):
    return not_implemented()


def create_new_user():
    return not_implemented()


def retrieve_ability_by_id(abilityId):
    for ability in abilities:
        if ability['id'] == abilityId:
            return ability, 200 # Return the ability object and a 200 OK status code

    return {"error": "Ability not found"}, 404  # Return an error message and a 404 Not Found status code


def retrieve_all_users():
    return retrieve_all(users)


def retrieve_all_abilities():
    return retrieve_all(abilities)

def retrieve_asset_by_id(assetId):

    for asset in assets:
        if asset['id'] == assetId:
            return asset, 200 # Return the asset object and a 200 OK status code

    return {"error": "Asset not found"}, 404  # Return an error message and a 404 Not Found status code


def retrieve_all_assets():
    return retrieve_all(assets)


# Get config item from database
def get_config_by_key(key):
    try:
        value = db.read_config_item(key)
        if value is None:
            return {"error": "Config item not found"}, 404

        # Parse the stored JSON back into a Python object
        value = json.loads(value)
        return value, 200
    except Exception as e:
        return {"error": str(e)}, 500


# Set config item in database
def set_config_by_key(key, body):
    try:
        # Convert body to JSON, even if it's a bare value
        body = json.dumps(body)
        db.set_config_item(key, body)
        return {"message": "Config item set successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 500


# Delete config item from database
def delete_config_by_key(key):
    try:
        db.delete_config_item(key)
        return '', 204
    except Exception as e:
        return {"error": str(e)}, 500
