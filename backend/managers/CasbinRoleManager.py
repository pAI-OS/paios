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
            ("user", "ADMIN_PORTAL", "ALL", "list"),
            ("user", "ADMIN_PORTAL", "ALL", "show"),
            ("admin", "ADMIN_PORTAL", "ALL", "list"),
            ("admin", "ADMIN_PORTAL", "ALL", "show"),
            ("admin", "ADMIN_PORTAL", "ALL", "create"),
            ("admin", "ADMIN_PORTAL", "ALL", "edit"),
            ("admin", "ADMIN_PORTAL", "ALL", "delete")
        ]
        
        for rule in default_rules:
            self.enforcer.add_policy(*rule)

    def get_enforcer(self):
        return self.enforcer
    
    def check_permissions(self, user_id, res_act, res_id, domain):
        return self.enforcer.enforce(user_id, domain, res_id, res_act)
    
    def get_permissions(self, role, domain):
        return self.enforcer.get_permissions_for_user_in_domain(role, domain)
    
    def create_resource_access(self, role, domain):
        permissions = self.get_permissions(role, domain)
        output = {}
        for _,_, resource, action in permissions:
            if resource not in output:
                output[resource] = []
            
            if action not in output[resource]:
                output[resource].append(action)

        return output
    
    def assign_user_role(self, user_id, domain, role="admin"):
        self.enforcer.add_role_for_user_in_domain(user_id, role, domain)

    def get_admin_users(self, domain):
        return self.enforcer.get_users_for_role_in_domain("admin",domain)

    def get_roles_for_user_in_domain(self, user_id, domain):
        return self.enforcer.get_roles_for_user_in_domain(user_id, domain)
    
    def get_user_role(self, user_id, domain):
        return ",".join(self.enforcer.get_roles_for_user_in_domain(user_id, domain))
        
