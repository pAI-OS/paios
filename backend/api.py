from flask import jsonify
import os
import signal
import subprocess
import json
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
# abilities = [
#     {
#         "id": "optical-character-recognition",
#         "name": "Optical Character Recognition",
#         "description": "Conversion of images to text"
#     }
# ]
abilities = []

abilities_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "abilities"))
for subdir in os.listdir(abilities_dir):
    if os.path.isdir(os.path.join(abilities_dir, subdir)):
        metadata_path = os.path.join(abilities_dir, subdir, "metadata.json")
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path) as f:
                    metadata = json.load(f)

                    # calculate dependency metadata
                    if 'dependencies' in metadata:
                        if 'resources' in metadata['dependencies']:
                            for resource in metadata['dependencies']['resources']:
                                resource_path = os.path.join(abilities_dir, subdir, resource['filename'])
                                if os.path.exists(resource_path):
                                    resource['localSize'] = os.path.getsize(resource_path)
                                if 'remoteSize' in resource and 'localSize' in resource:
                                    resource['percentComplete'] = round((resource['localSize'] / resource['remoteSize']) * 100, 2)

                    # dictionary of abilities keyed by id needs to be converted to list of objects for react-admin's Datagrid
                    # abilities[metadata.get("id")] = metadata
                    abilities.append(metadata)
           
            except (FileNotFoundError, json.JSONDecodeError):
                pass

# Helper functions for common responses
def get_ability(abilityId):
    for ability in abilities:
        if ability["id"] == abilityId: return ability
    return None

def get_ability_dependency(abilityId, dependencyId):
    ability = get_ability(abilityId)
    if not ability: return None
    for dependency in ability["dependencies"]["resources"]:
        if dependency["id"] == dependencyId: return dependency
    return None

def ability_dependency_download_start(abilityId, dependencyId): 
    import threading
    import requests
    import time
    import os

    # threads check if they should keep running on each loop
    timeout = 60*60*24 # one day in seconds

    try:
        ability = get_ability(abilityId)
        dependency = next((item for item in ability["dependencies"]["resources"] if item["id"] == dependencyId), None)
        url = dependency["url"]
        dependency["localFile"] = os.path.join(abilities_dir, abilityId, dependency["filename"])
        dependency["keepDownloading"] = True
    except KeyError:
        print(f"An error occurred downloading ability {abilityId} dependency {dependencyId}")
        return

    def download_file():
        #print("Downloading " + url + " to " + dependency["localFile"])
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(dependency["localFile"], 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    if chunk: 
                        f.write(chunk)
                    keep_downloading()
        del(dependency["keepDownloading"])

    def update_progress():
        while time.time() - start_time < timeout: # give up after timeout
            try:
                if os.path.exists(dependency["localFile"]):
                    # sleep first so thread doesn't exit immediately on first loop (e.g. re-downloading)
                    time.sleep(1)
                    dependency["localSize"] = os.path.getsize(dependency["localFile"])
                    dependency["percentComplete"] = round((dependency["localSize"] / dependency["remoteSize"]) * 100, 2)
                    if (dependency["localSize"] == dependency["remoteSize"]):
                        print("Already downloaded " + dependency["localFile"])
                        return # download complete so exit thread
                    keep_downloading()
            except KeyError as e:
                print(f"An error occurred updating progress of ability {abilityId} dependency {dependencyId} download: {e}")
                return


    def keep_downloading():
        # give up and exit thread after timeout
        if time.time() - start_time > timeout: return
        # exit thread if keepDownloading is False or removed
        dependency = get_ability_dependency(abilityId, dependencyId)
        if not dependency or not dependency.get('keepDownloading'): return

    start_time = time.time()
    threading.Thread(target=download_file).start()
    threading.Thread(target=update_progress).start()


def ability_dependency_download_stop(abilityId, dependencyId): 
    # sets keepDownloading to False to stop download thread
    dependency = get_ability_dependency(abilityId, dependencyId)
    if dependency:
        dependency["keepDownloading"] = False


def ability_dependency_download_delete(abilityId, dependencyId): 
    # deletes local file
    dependency = get_ability_dependency(abilityId, dependencyId)
    if dependency:
        try:
            os.remove(dependency["localFile"])
        except FileNotFoundError:
            pass


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


# Helper functions for common responses
def ok(): return {"message": "OK"}, 200
def not_implemented(): return {"message": "This operation is not implemented yet."}, 501
def retrieve_all(payload, status_code=200): return jsonify(payload), status_code, {'X-Total-Count': len(payload)}

# OPTIONS are required for CORS preflight requests
def options_abilities(): return ok()
def options_abilities_abilityid(): return ok()
def options_abilities_abilityid_start(): return ok()
def options_abilities_abilityid_stop(): return ok()
def options_ability_dependency_download_start(): return ok()
def options_ability_dependency_download_stop(): return ok()
def options_ability_dependency_download_delete(): return ok()
def options_assets(): return ok()
def options_assets_assetid(): return ok()
def options_config(): return ok()
def options_user(): return ok()
def options_users(): return ok()
def options_users_userid(): return ok()

# Not implemented yet
def update_user_by_id(userId): return not_implemented()
def create_new_user(): return not_implemented()

# Retrieve all
def retrieve_all_users(): return retrieve_all(users)
def retrieve_all_abilities(): return retrieve_all(abilities)
def retrieve_all_assets(): return retrieve_all(assets)

# Retrieve by ID
def retrieve_user_by_id(userId):

    for user in users:
        if user['id'] == userId:
            return user, 200
    
    return {"error": "User not found"}, 404

def retrieve_ability_by_id(abilityId):
    ability = get_ability(abilityId)
    if ability:
        return ability, 200
    else:
        return {"error": "Ability not found"}, 404

def retrieve_asset_by_id(assetId):

    for asset in assets:
        if asset['id'] == assetId:
            return asset, 200

    return {"error": "Asset not found"}, 404

# Abilities Management
def start_ability(abilityId):
    print(f"Starting ability {abilityId}")
    ability = get_ability(abilityId)
    start_script = ability.get('scripts', {}).get('start')

    if start_script is None:
        return {"error": "Ability not found or start script not set"}, 404

    # Start the subprocess and store the PID in the ability dictionary
    process = subprocess.Popen([os.path.join('..', 'abilities', abilityId, start_script)], shell=True)
    ability['pid'] = process.pid
    return ok()

def stop_ability(abilityId):
    ability = get_ability(abilityId)
    if not ability: return {"error": "Ability not found"}, 404
    if 'pid' in ability:
        # Terminate the subprocess
        os.kill(ability['pid'], signal.SIGTERM)
        del ability['pid']  # Remove the pid from the ability dictionary
        return ok()
    else:
        return {"error": "Ability not running"}, 404


# Configuration Management

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
