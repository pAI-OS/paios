# import all the views to satisfy Connexion's MethodView resolver
# otherwise connexion will throw "TypeError: 'module' object is not callable"
from .AbilitiesView import AbilitiesView
from .AssetsView import AssetsView
from .ChannelsView import ChannelsView
from .ConfigView import ConfigView
from .DownloadsView import DownloadsView
from .UsersView import UsersView
from .AuthView import AuthView
