from abc import ABC, abstractmethod

class Dependency(ABC):
    def __init__(self, ability, dependency):
        self.ability = ability
        self.dependency = dependency

    @abstractmethod
    def refresh_status(self):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass
