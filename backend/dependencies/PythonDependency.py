from .Dependency import Dependency
import pkg_resources
import requests
import subprocess
import sys
import importlib
from packaging.specifiers import SpecifierSet
from packaging.version import Version

class PythonDependency(Dependency):
    def refresh_status(self):
        package_name = self.dependency.get('id')
        version_specifier = self.dependency.get('version', '')

        versions = {}

        installed_version = self._get_installed_version(package_name)
        if installed_version:
            versions['installed'] = installed_version

        available_versions = self._get_available_versions(package_name)
        if available_versions:
            versions['all'] = available_versions
            satisfactory_versions = self._get_satisfactory_versions(available_versions, version_specifier)
            if satisfactory_versions:
                versions['satisfactory'] = satisfactory_versions

            latest_version = self._get_latest_version(available_versions)
            if latest_version:
                versions['latest'] = latest_version

        if versions:
            self.dependency['versions'] = versions

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
        except requests.RequestException:
            return None

    def _get_satisfactory_versions(self, available_versions, version_specifier):
        if not available_versions:
            return None
        try:
            specifier = SpecifierSet(version_specifier)
            return [version for version in available_versions if specifier.contains(Version(version))]
        except Exception:
            return None

    def _get_latest_version(self, available_versions):
        if not available_versions:
            return None
        return available_versions[0]

    def install(self):
        package_name = self.dependency.get('id')
        version_specifier = self.dependency.get('version', '')

        def reload_package(package_name):
            try:
                package_module = importlib.import_module(package_name)
                importlib.reload(package_module)
            except ImportError:
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

        if version_specifier:
            if not version_specifier.startswith(('==', '>=', '<=', '~=', '!=')):
                version_specifier = '==' + version_specifier
        else:
            version_specifier = ''

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

            reload_package(package_name)

            package_version = get_installed_package_version(package_name)
            self.dependency['version-installed'] = package_version
            self.dependency['satisfied'] = True

            return {"message": f"Successfully installed {package_with_version} ({package_version})."}, 200
        except (subprocess.CalledProcessError, pkg_resources.DistributionNotFound, ImportError) as e:
            return {"error": f"Failed to install {package_with_version}.", "details": str(e)}, 500

    def start(self):
        pass

    def stop(self):
        pass
