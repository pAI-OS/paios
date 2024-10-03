# import all the views to satisfy Connexion's MethodView resolver
# otherwise connexion will throw "TypeError: 'module' object is not callable"
from .AbilitiesView import AbilitiesView
from .CollectionsView import CollectionsView
from .ResourcesView import ResourcesView
from .ConfigView import ConfigView
from .DownloadsView import DownloadsView
from .UsersView import UsersView
from .PersonasView import PersonasView
from .SharesView import SharesView
from .AuthView import AuthView
