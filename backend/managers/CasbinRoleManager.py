from casbin import Enforcer
from casbin_sqlalchemy_adapter import Adapter
from pathlib import Path
from common.paths import db_path
from threading import Lock

class CasbinRoleManager:
    _instance = None
    _lock = Lock()  # Add this line if you want thread safety

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(CasbinRoleManager, cls).__new__(cls)
                    cls._instance.init_casbin()
        return cls._instance

    def init_casbin(self):
        path = Path(db_path)  # Ensure correct path
        adapter = Adapter(f"sqlite:///{path}")  # Format as SQLite URL
        model_path = str(Path(__file__).parent.parent / 'rbac_model.conf')  # Convert to string
        self.enforcer = Enforcer(model_path, adapter)  # Use Enforcer correctly
        self.add_default_rules()

    def add_default_rules(self):
        default_rules = [
            ("user", "DEFAULT", "list"),
            ("user", "DEFAULT", "show"),
            ("admin", "DEFAULT", "create"),
            ("admin", "DEFAULT", "edit"),
            ("admin", "DEFAULT", "delete")
        ]
        
        for rule in default_rules:
            self.enforcer.add_policy(*rule)
        
        self.enforcer.add_grouping_policy("admin", "user")

    def get_enforcer(self):
        return self.enforcer
    
    def check_permissions(self, role, resource, resource_type):
        return self.enforcer.enforce(role, resource, resource_type)
    
    def get_permissions(self, role="user"):
        return self.enforcer.get_implicit_permissions_for_user(role)
    
    def create_resource_access(self, role):
        permissions = self.get_permissions(role)

        output = {}
        for _, resource, action in permissions:
            if resource not in output:
                output[resource] = []
            
            if action not in output[resource]:
                output[resource].append(action)

        return output
        
