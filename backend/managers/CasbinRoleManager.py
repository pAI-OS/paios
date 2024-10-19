import casbin
from casbin_sqlalchemy_adapter import Adapter
from pathlib import Path
from common.paths import db_path

class CasbinRoleManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CasbinRoleManager, cls).__new__(cls)
            cls._instance.init_casbin()
        return cls._instance

    def init_casbin(self):
        adapter = Adapter(db_path)
        model_path = Path(__file__).parent.parent / 'rbac_model.conf'
        self.enforcer = casbin.Enforcer(str(model_path), adapter)
    
    def get_enforcer(self):
        return self.enforcer
