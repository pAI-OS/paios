# List of users
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
abilities = [
    {
        "id": "optical-character-recognition",
        "name": "Optical Character Recognition",
        "description": "Conversion of images to text"
    },
    {
        "id": "vector-database",
        "name": "Vector Database",
        "description": "Stores vectors (fixed-length lists of numbers) along with other data items"
    }
]

# List of assets
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

def get_user_by_id(userId):

    for user in users:
        if user['id'] == userId:
            return user, 200  # Return the user object and a 200 OK status code
        
    return {"error": "User not found"}, 404  # Return an error message and a 404 Not Found status code

def not_implemented():
    return {"message": "This operation is not implemented yet."}, 501

def patch_user_by_id(userId):
    return not_implemented()

def create_new_user():
    return not_implemented()

def get_abilities_by_id(abilityId):
    for ability in abilities:
        if ability['id'] == abilityId:
            return ability, 200 # Return the ability object and a 200 OK status code

    return {"error": "Ability not found"}, 404  # Return an error message and a 404 Not Found status code

def retrieve_all_users():
    return users, 200 # Return the user objects and a 200 OK status code

def retrieve_all_abilities():
    return abilities, 200 # Return the ability objects and a 200 OK status code

def get_asset_by_id(assetId):

    for asset in assets:
        if asset['id'] == assetId:
            return asset, 200 # Return the asset object and a 200 OK status code

    return {"error": "Asset not found"}, 404  # Return an error message and a 404 Not Found status code

def retrieve_all_assets():
    return assets, 200 # Return the asset objects and a 200 OK status code
