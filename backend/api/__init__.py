# import all the views to satisfy Connexion's MethodView resolver
# otherwise connexion will throw "TypeError: 'module' object is not callable"
from .AbilitiesView import AbilitiesView
from .ChannelsView import ChannelsView
from .ConfigView import ConfigView
from .UsersView import UsersView
