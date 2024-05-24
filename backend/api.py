from flask import jsonify
import os
import sys
import signal
import subprocess
import shlex
import packaging
import pkg_resources
from pathlib import Path
import json
from paths import venv_bin_dir, abilities_dir, abilities_data_dir

# List of abilities
# abilities = [
#     {
#         "id": "optical-character-recognition",
#         "name": "Optical Character Recognition",
#         "description": "Conversion of images to text"
#     }
# ]
abilities = []

for ability in os.listdir(abilities_dir):
    if os.path.isdir(os.path.join(abilities_dir, ability)):
        metadata_path = os.path.join(abilities_dir, ability, "metadata.json")
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path) as f:
                    metadata = json.load(f)

                    # calculate dependency metadata
                    if 'dependencies' in metadata:
                        if 'resources' in metadata['dependencies']:
                            for resource in metadata['dependencies']['resources']:
                                resource_path = os.path.join(abilities_data_dir, ability, resource['filename'])
                                if os.path.exists(resource_path):
                                    resource['localSize'] = os.path.getsize(resource_path)
                                if 'remoteSize' in resource and 'localSize' in resource:
                                    resource['percentComplete'] = round((resource['localSize'] / resource['remoteSize']) * 100, 2)

                        from packaging.specifiers import SpecifierSet
                        if 'python' in metadata['dependencies']:
                            for dependency in metadata['dependencies']['python']:
                                
                                package_name = dependency['id']
                                version_requirement = dependency['version']
                                specifier = SpecifierSet(version_requirement)

                                try:
                                    package_version = pkg_resources.get_distribution(package_name).version
                                    if package_version: dependency['installed'] = True
                                    dependency['version-installed'] = package_version
                                    if specifier.contains(package_version):
                                        dependency['satisfied'] = True
                                except (packaging.specifiers.InvalidSpecifier):
                                    print(f"Invalid specifier for {ability}: {version_requirement}")
                                except (packaging.version.InvalidVersion, pkg_resources.DistributionNotFound) as e:
                                        dependency['installed'] = False
                                        dependency['satisfied'] = False
                                        if 'version-installed' in dependency:
                                            del dependency['version-installed']

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

def get_ability_dependency(abilityId, dependencyId, dependencyType):
    ability = get_ability(abilityId)
    if not ability: return None
    for dependency in ability["dependencies"][dependencyType]:
        if dependency["id"] == dependencyId: return dependency
    return None

def ability_python_dependency_install(abilityId, dependencyId):
    import importlib
    import subprocess
    import sys

    # reloads newly installed package into memory without updating 
    def reload_package(package_name):
        try:
            package_module = importlib.import_module(package_name)
            importlib.reload(package_module)
        except ImportError as e:
            # print(f"Error importing {package_name}: {e}") # which is to be expected if the module was not already loaded before updating
            pass
        except Exception as e:
            print(f"Error reloading {package_name}: {e}")


    def get_installed_package_version(package_name):
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'show', package_name], text=True, stdout=subprocess.PIPE)
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    return line.split('Version:')[1].strip()
        except subprocess.CalledProcessError as e:
            print(f"Failed to retrieve package version for {package_name}: {e}")
        except Exception as e:
            print(f"Unexpected error occurred while retrieving package version for {package_name}: {e}")
        return None


    def install_python_package(package_name, version_specifier=None):
        # Ensure the version specifier is properly formatted
        if version_specifier:
            if not version_specifier.startswith(('==', '>=', '<=', '~=', '!=')):
                version_specifier = '==' + version_specifier  # Default to exact version if no relational operator is specified
        else:
            version_specifier = ''  # If no version is specified, install the latest available version

        # Construct the package installation command with version specifier
        package_with_version = f"{package_name}{version_specifier}"
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', package_with_version],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(result.stdout)
            print(result.stderr)

            # reload package in running interpreter (or it will return the old version on upgrades)
            reload_package(package_name)

            # Update version-installed
            #package_version = pkg_resources.get_distribution(package_name).version
            package_version = get_installed_package_version(package_name)
            dependency['version-installed'] = package_version
            dependency['satisfied'] = True

            return {"message": f"Successfully installed {package_with_version} ({package_version})."}, 200
        except (subprocess.CalledProcessError, pkg_resources.DistributionNotFound, ImportError) as e:
            return {"error": f"Failed to install {package_with_version}.", "details": e.stderr}, 500

    dependency = get_ability_dependency(abilityId, dependencyId, "python")
    if not dependency:
        return {"error": "Dependency not found"}, 404
    package_id = dependency.get('id')
    version_specifier = dependency.get('version', None)
    if not package_id:
        return {"error": "Package ID not found for dependency"}, 404

    return install_python_package(package_id, version_specifier)


def ability_resource_dependency_download_start(abilityId, dependencyId): 
    import threading
    import requests
    import time
    import os

    # threads check if they should keep running on each loop
    timeout = 60*60*24 # one day in seconds
    ability_data_dir = os.path.join(abilities_data_dir, abilityId)
    local_file = ''

    try:
        dependency = get_ability_dependency(abilityId, dependencyId, "resource")
        url = dependency["url"]
        local_file = os.path.join(ability_data_dir, dependency["filename"])

        dependency["keepDownloading"] = True
    except KeyError:
        print(f"An error occurred downloading ability {abilityId} dependency {dependencyId}")
        return

    def download_file():
        #print("Downloading " + url + " to " + dependency["localFile"])
        os.makedirs(ability_data_dir, exist_ok=True)
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    if chunk: 
                        f.write(chunk)
                    keep_downloading()
        if "keepDownloading" in dependency: del(dependency["keepDownloading"])

    def update_progress():
        while time.time() - start_time < timeout: # give up after timeout
            try:
                if os.path.exists(local_file):
                    # sleep first so thread doesn't exit immediately on first loop (e.g. re-downloading)
                    time.sleep(1)
                    dependency["localSize"] = os.path.getsize(local_file)
                    dependency["percentComplete"] = round((dependency["localSize"] / dependency["remoteSize"]) * 100, 2)
                    if (dependency["localSize"] == dependency["remoteSize"]):
                        #print("Already downloaded " + local_file)
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


def ability_resource_dependency_download_stop(abilityId, dependencyId): 
    # sets keepDownloading to False to stop download thread
    dependency = get_ability_dependency(abilityId, dependencyId, "resource")
    if dependency:
        if "keepDownloading" in dependency:
            del dependency["keepDownloading"]


def ability_resource_dependency_download_delete(abilityId, dependencyId): 
    # deletes local file
    dependency = get_ability_dependency(abilityId, dependencyId, "resource")
    ability_data_dir = os.path.join(abilities_data_dir, abilityId)
    local_file = os.path.join(ability_data_dir, dependency["filename"])
    if dependency:
        try:
            os.remove(local_file)
            if "localSize" in dependency: del dependency["localSize"]
            if "keepDownloading" in dependency: del dependency["keepDownloading"] # in case it was stopped
        except FileNotFoundError:
            pass


# List of assets
# TODO: These should be read from storage sources like local directory, S3, NAS, Solid pod, etc.
assets = [
  {
    "id": 523,
    "title": "Attention Is All You Need",
    "userId": "5bae4a90-ce69-4483-86ef-d723258f21e5",
    "creator": "Ashish Vaswani et al",
    "subject": "Artificial Intelligence",
    "description": "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely."
  },
  {
    "id": 952,
    "title": "Generative Adversarial Networks",
    "userId": "1cbb0bc5-bae2-4b9d-9555-f2282f767047",
    "creator": "Goodfellow et al",
    "subject": "Artificial Intelligence",
    "description": "We propose a new framework for estimating generative models via an adversarial process, in which we simultaneously train two models: a generative model G that captures the data distribution, and a discriminative model D that estimates the probability that a sample came from the training data rather than G."
  }
]


# Helper functions for common responses
def ok(): return {"message": "OK"}, 200
def not_implemented(): return {"message": "This operation is not implemented yet."}, 501
def retrieve_all(payload, status_code=200): return jsonify(payload), status_code, {'X-Total-Count': len(payload)}

# TODO: we need a better way to deal with OPTIONS requests required by CORS; can't automate this with connexion apparently
# OPTIONS are required for CORS preflight requests
def options_abilities(): return ok()
def options_abilities_abilityid(): return ok()
def options_abilities_abilityid_start(): return ok()
def options_abilities_abilityid_stop(): return ok()
def options_ability_resource_dependency_download_start(): return ok()
def options_ability_resource_dependency_download_stop(): return ok()
def options_ability_resource_dependency_download_delete(): return ok()
def options_ability_python_dependency_install(): return ok()
def options_assets(): return ok()
def options_assets_assetid(): return ok()
def options_channels(): return ok()
def options_channels_channelid(): return ok()
def options_config(): return ok()
def options_user(): return ok()
def options_users(): return ok()
def options_users_userid(): return ok()

# Retrieve all
def retrieve_all_abilities(): return retrieve_all(abilities)
def retrieve_all_assets(): return retrieve_all(assets)

# Retrieve by ID
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
    import stat

    print(f"Starting ability {abilityId}")
    ability = get_ability(abilityId)
    if ability is None: return {"error": "Ability not found"}, 404

    start_script = ability.get('scripts', {}).get('start', '')
    if start_script is None: return {"error": "Ability start script not set"}, 404

    start_script_parts = shlex.split(start_script)
    #start_script_argv0 = start_script_parts[0] # if start_script_parts else None
    #start_script_args = start_script_parts[1:] if len(start_script_parts) > 1 else []

    if start_script_parts is None:
        return {"error": "Unable to determine start script executable"}, 500

    # find the start script in the ability's directory or the ability's data directory
    search_paths = [abilities_dir / abilityId, abilities_data_dir / abilityId, venv_bin_dir ]
    script_found = False
    for path in search_paths:
        start_script_candidate = os.path.join(path, start_script_parts[0])
        if os.path.exists(start_script_candidate):
            start_script_cwd = path
            start_script_parts[0] = start_script_candidate
            script_found = True
            break
    if not script_found: return {"error": f"Start script {start_script_parts[0]} not found in {search_paths}"}, 404

    # Set the execute bit on the start script if it's not already set (e.g. fresh clone from git)
    if os.name == "posix": # Linux, macOS, etc.
        if not os.access(start_script_path, os.X_OK):
            current_permissions = stat.S_IMODE(os.lstat(start_script_path).st_mode)
            try:
                print(f"Warning: Setting execute bit on {start_script_path}")
                os.chmod(start_script_path, current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            except Exception as e:
                print(f"Warning: Failed to set execute bit on start script: {e}")

    # Prepend the Python executable to the start script if it's a Python script rather than relying on associations or shebang
    if start_script_parts[0].endswith('.py'):
        python_executable = str(Path(sys.executable))
        start_script_parts.insert(0, python_executable)

    # Define file paths for stdout and stderr
    stdout_file_path = Path(start_script_cwd) / f"{abilityId}_stdout.log"
    stderr_file_path = Path(start_script_cwd) / f"{abilityId}_stderr.log"

    # Open file handles
    stdout_file = open(stdout_file_path, 'w')
    stderr_file = open(stderr_file_path, 'w')

    # Start the subprocess and store the PID in the ability dictionary
    process = subprocess.Popen(start_script_parts, cwd=start_script_cwd, shell=False, stdout=stdout_file, stderr=stderr_file, text=True)
    ability['pid'] = process.pid
    return ok()

def stop_ability(abilityId):
    ability = get_ability(abilityId)
    if not ability: return {"error": "Ability not found"}, 404
    if 'pid' in ability:
        # Terminate the subprocess
        try:
            os.kill(ability['pid'], signal.SIGTERM)
        except ProcessLookupError:
            return {"error": "Ability not running"}, 404
        del ability['pid']  # Remove the pid from the ability dictionary
        return ok()
    else:
        return {"error": "Ability not running"}, 404
