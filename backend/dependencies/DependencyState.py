from enum import Enum

class DependencyState(Enum):
    AVAILABLE = "available"
    INSTALLING = "installing"
    INSTALLED = "installed"
    FAILED = "failed"
