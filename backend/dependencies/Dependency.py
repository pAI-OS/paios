from abc import ABC, abstractmethod

class Dependency(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def refresh_status(self, ability, dependency):
        pass

    @abstractmethod
    def start(self, ability, dependency):
        pass

    @abstractmethod
    def stop(self, ability, dependency):
        pass
