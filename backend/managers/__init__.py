from .AbilitiesManager import AbilitiesManager
from .AssetsManager import AssetsManager
from .ChannelsManager import ChannelsManager
from .ConfigManager import ConfigManager
from .DownloadsManager import DownloadsManager
from .UsersManager import UsersManager
from .AuthManager import AuthManager

# List of manager classes
manager_classes = [
    AbilitiesManager,
    AssetsManager,
    ChannelsManager,
    ConfigManager,
    DownloadsManager,
    UsersManager,
    AuthManager
]

# Initialize the managers dynamically
managers = {cls.__name__.lower(): cls() for cls in manager_classes}

# Expose the initialized managers for easy access as e.g. backend.managers.managers['abilitiesmanager']
__all__ = ['managers'] + list(managers.keys())
