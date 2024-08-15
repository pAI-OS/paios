from .AbilitiesManager import AbilitiesManager
from .AssetsManager import AssetsManager
from .ResourcesManager import ResourcesManager
from .ConfigManager import ConfigManager
from .DownloadsManager import DownloadsManager
from .UsersManager import UsersManager
from .PersonasManager import PersonasManager
from .AuthManager import AuthManager
from .RagManager import RagManager

# List of manager classes
manager_classes = [
    AbilitiesManager,
    AssetsManager,
    ResourcesManager,
    ConfigManager,
    DownloadsManager,
    UsersManager,
    AuthManager,
    PersonasManager,
    RagManager
]

# Initialize the managers dynamically
managers = {cls.__name__.lower(): cls() for cls in manager_classes}

# Expose the initialized managers for easy access as e.g. backend.managers.managers['abilitiesmanager']
__all__ = ['managers'] + list(managers.keys())
