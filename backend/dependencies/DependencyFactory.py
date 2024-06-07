from .ResourceDependency import ResourceDependency
from .PythonDependency import PythonDependency
from .LinuxDependency import LinuxDependency
from .ContainerDependency import ContainerDependency

class DependencyFactory:
    @staticmethod
    def create_dependency(ability, dependency):
        dependency_id = dependency.get('id')
        dependency_type = dependency.get('type')
        
        if dependency_type == 'resource':
            return ResourceDependency(ability, dependency)
        elif dependency_type == 'python':
            return PythonDependency(ability, dependency)
        elif dependency_type == 'linux':
            return LinuxDependency(ability, dependency)
        elif dependency_type == 'container':
            return ContainerDependency(ability, dependency)
        else:
            raise ValueError(f"Unknown dependency type: {dependency_type}")
