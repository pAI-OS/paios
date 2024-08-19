from .AbilitiesManager import AbilitiesManager
from .AssetsManager import AssetsManager
from .ResourcesManager import ResourcesManager
from .ConfigManager import ConfigManager
from .DownloadsManager import DownloadsManager
from .UsersManager import UsersManager
from .PersonasManager import PersonasManager
from .RagManager import RagManager
from .MessagesManager import MessagesManager
from .ConversationsManager import ConversationsManager

# List of manager classes
manager_classes = [
    AbilitiesManager,
    AssetsManager,
    ResourcesManager,
    ConfigManager,
    DownloadsManager,
    UsersManager,
    PersonasManager,
    RagManager,
    MessagesManager,
    ConversationsManager
]

# Initialize the managers dynamically
managers = {cls.__name__.lower(): cls() for cls in manager_classes}

# Expose the initialized managers for easy access as e.g. backend.managers.managers['abilitiesmanager']
__all__ = ['managers'] + list(managers.keys())
