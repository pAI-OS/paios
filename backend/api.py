#
#
# THIS IS A DEPRECATED FILE ACTIVELY BEING MIGRATED TO THE MANAGER INFRASTRUCTURE
#
#
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
                                resource_path = os.path.join(abilities_data_dir, ability, resource['file_name'])
                                if os.path.exists(resource_path):
                                    resource['localSize'] = os.path.getsize(resource_path)
                                if 'file_size' in resource and 'localSize' in resource:
                                    resource['percentComplete'] = round((resource['localSize'] / resource['file_size']) * 100, 2)

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
def get_ability(ability_id):
    for ability in abilities:
        if ability["id"] == ability_id: return ability
    return None

def get_ability_dependency(ability_id, dependency_id, dependency_type):
    # print(f"Getting dependency {dependency_id} of type {dependency_type} for ability {ability_id}")
    ability = get_ability(ability_id)
    # print(f"Ability: {ability}")
    if not ability: return None
    if dependency_type not in ability["dependencies"]:
        # print(f"Dependency type {dependency_type} not found for ability {ability_id}")
        return None
    for dependency in ability["dependencies"][dependency_type]:
        # print(f"Dependency: {dependency}")
        if dependency["id"] == dependency_id: return dependency
    return None

def ability_python_dependency_install(ability_id, dependency_id):
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

    dependency = get_ability_dependency(ability_id, dependency_id, "python")
    if not dependency:
        return {"error": "Dependency not found"}, 404
    package_id = dependency.get('id')
    version_specifier = dependency.get('version', None)
    if not package_id:
        return {"error": "Package ID not found for dependency"}, 404

    return install_python_package(package_id, version_specifier)
