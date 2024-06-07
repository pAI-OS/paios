from .Dependency import Dependency

class LinuxDependency(Dependency):
    # TODO: Linux dependencies need to be implemented when required
    def refresh_status(self):
        raise NotImplementedError
        #package_name = self.dependency.get('name')
        #import subprocess
        #result = subprocess.run(['dpkg', '-s', package_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #self.dependency['status'] = result.returncode == 0

    def start(self):
        pass

    def stop(self):
        pass
