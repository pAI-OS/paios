from .Dependency import Dependency

class ContainerDependency(Dependency):
    def refresh_status(self):
        # TODO: Linux dependencies need to be implemented when required
        raise NotImplementedError
        #container_name = self.dependency.get('name')
        #import docker
        #client = docker.from_env()
        #try:
        #    container = client.containers.get(container_name)
        #    self.dependency['status'] = container.status == 'running'
        #except docker.errors.NotFound:
        #    self.dependency['status'] = False

    def start(self):
        pass

    def stop(self):
        pass
