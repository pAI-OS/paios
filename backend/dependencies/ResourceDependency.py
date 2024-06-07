import os
from .Dependency import Dependency

class ResourceDependency(Dependency):
    def refresh_status(self):
        resource_path = self.dependency.get('path')
        self.dependency['status'] = os.path.exists(resource_path)

    def start(self):
        pass

    def stop(self):
        pass
