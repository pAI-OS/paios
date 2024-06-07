from .Dependency import Dependency

class PythonDependency(Dependency):
    def refresh_status(self):
        package_name = self.dependency.get('id')
        import pkg_resources
        try:
            pkg_resources.get_distribution(package_name)
            self.dependency['status'] = True
        except pkg_resources.DistributionNotFound:
            self.dependency['status'] = False

    def start(self):
        pass

    def stop(self):
        pass
