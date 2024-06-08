from backend.dependencies.Dependency import Dependency
import asyncio
import pkg_resources
import requests
import subprocess
import sys
import importlib
from packaging.specifiers import SpecifierSet
from packaging.version import Version

import logging
logger = logging.getLogger(__name__)

class PythonDependency(Dependency):
    def refresh_status(self, ability, dependency):
        package_name = dependency.get('id')
        required_version = dependency.get('required', '')

        versions = dependency.get('versions', {})

        self._refresh_versions(package_name, required_version, versions)

        if versions:
            dependency['versions'] = versions

    def _refresh_versions(self, package_name, required_version, versions):
        installed_version = self._get_installed_version(package_name)
        if installed_version:
            versions['installed'] = installed_version

        available_versions = self._get_available_versions(package_name)
        if available_versions:
            versions['all'] = available_versions
            satisfactory_versions = self._get_satisfactory_versions(available_versions, required_version)
            if satisfactory_versions:
                versions['satisfactory'] = satisfactory_versions

            latest_version = self._get_latest_version(available_versions)
            if latest_version:
                versions['latest'] = latest_version

        # Ensure satisfactory versions are set
        if 'satisfactory' not in versions:
            versions['satisfactory'] = self._get_satisfactory_versions(available_versions, required_version)

        # Add satisfied flag
        satisfied = self._is_satisfied(installed_version, versions['satisfactory'])
        logger.debug(f"Setting satisfied for {package_name}: {satisfied}")
        versions['satisfied'] = satisfied

    def _is_satisfied(self, installed_version, satisfactory_versions):
        if not installed_version or not satisfactory_versions:
            logger.debug(f"Installed version or satisfactory versions are missing: installed_version={installed_version}, satisfactory_versions={satisfactory_versions}")
            return False
        is_satisfied = installed_version in satisfactory_versions
        logger.debug(f"Checking if installed version {installed_version} is in satisfactory versions {satisfactory_versions}: {is_satisfied}")
        return is_satisfied

    def _get_installed_version(self, package_name):
        try:
            dist = pkg_resources.get_distribution(package_name)
            return dist.version
        except pkg_resources.DistributionNotFound:
            return None

    def _get_available_versions(self, package_name):
        try:
            response = requests.get(f'https://pypi.org/pypi/{package_name}/json')
            response.raise_for_status()
            data = response.json()
            return sorted(data['releases'].keys(), key=Version, reverse=True)
        except requests.RequestException as e:
            logger.error(f"Error fetching available versions for {package_name}: {e}")
            return None

    def _get_satisfactory_versions(self, available_versions, required_version):
        if not available_versions:
            return None
        try:
            specifier = SpecifierSet(required_version)
            return [version for version in available_versions if specifier.contains(Version(version))]
        except Exception as e:
            logger.error(f"Error getting satisfactory versions: {e}")
            return None

    def _get_latest_version(self, available_versions):
        if not available_versions:
            return None
        return available_versions[0]

    async def install(self, ability, dependency):
        package_name = dependency.get('id')
        required_version = dependency.get('required', '')

        if required_version:
            if not required_version.startswith(('==', '>=', '<=', '~=', '!=')):
                required_version = '==' + required_version
        else:
            required_version = ''

        package_with_version = f"{package_name}{required_version}"

        def run_subprocess():
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', package_with_version],
                    capture_output=True,
                    text=True
                )
                return result
            except Exception as e:
                logger.error(f"Subprocess execution failed: {e}")
                raise

        def reload_package(package_name):
            try:
                package_module = importlib.import_module(package_name)
                importlib.reload(package_module)
            except ImportError:
                pass
            except Exception as e:
                logger.error(f"Error reloading {package_name}: {e}")

        def get_installed_package_version(package_name):
            try:
                result = subprocess.run([sys.executable, '-m', 'pip', 'show', package_name], text=True, stdout=subprocess.PIPE)
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        return line.split('Version:')[1].strip()
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to retrieve package version for {package_name}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error occurred while retrieving package version for {package_name}: {e}")
            return None

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, run_subprocess)
            if result.returncode == 0:
                logger.info(f"Successfully installed {package_with_version}")
                reload_package(package_name)
                package_version = get_installed_package_version(package_name)
                dependency['version-installed'] = package_version
                dependency['satisfied'] = self._is_satisfied(package_version, dependency['versions'].get('satisfactory', []))
                return {"message": f"Successfully installed {package_with_version} ({package_version})."}
            else:
                error_message = result.stderr
                logger.error(f"Failed to install {package_with_version}: {error_message}")
                raise ValueError(f"Installation failed: {error_message}")
        except asyncio.CancelledError:
            logger.warning(f"Installation of {package_with_version} was cancelled")
            raise ValueError(f"Installation of {package_with_version} was cancelled")
        except pkg_resources.ContextualVersionConflict as e:
            logger.error(f"Version conflict during installation of {package_with_version}: {e}")
            raise ValueError(f"Version conflict: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during dependency installation: {e}", exc_info=True)
            raise ValueError(f"An unexpected error occurred: {str(e)}")

    def start(self, ability, dependency):
        pass

    def stop(self, ability, dependency):
        pass
