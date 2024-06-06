import json
import re
from backend.paths import abilities_dir
from enum import Enum

class AbilityState(Enum):
    AVAILABLE = "available"
    INSTALLING = "installing"
    INSTALLED = "installed"
    UNINSTALLING = "uninstalling"

class AbilitiesManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AbilitiesManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._load_abilities()
        return cls._instance

    def _load_abilities(self):
        self.abilities = self._fetch_abilities_from_directory()

    def _fetch_abilities_from_directory(self):
        abilities = []
        for ability_path in abilities_dir.iterdir():
            if ability_path.is_dir():
                ability_id = ability_path.name
                versions_info = self._get_versions_info(ability_path)
                version_to_load = versions_info['installed'] or versions_info['latest']
                if version_to_load:
                    ability_data = self._fetch_ability_from_directory(ability_path, version_to_load)
                    if ability_data:
                        if 'versions' in ability_data:
                            ability_data['versions'].update(versions_info)
                        else:
                            ability_data['versions'] = versions_info
                        abilities.append(ability_data)
        return abilities

    def _fetch_ability_from_directory(self, ability_path, version):
        version_dir = ability_path / version
        metadata_file = version_dir / 'metadata.json'
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                return metadata
        return None

    def _get_versions_info(self, ability_path):
        semver_pattern = re.compile(r'^\d+\.\d+\.\d+$')
        versions = []
        installed_version = None

        for version_dir in ability_path.iterdir():
            if version_dir.is_dir() and semver_pattern.match(version_dir.name):
                versions.append(version_dir.name)
            elif version_dir.is_file() and version_dir.name == 'installed':
                with open(version_dir, 'r') as f:
                    installed_version = f.read().strip()

        latest_version = max(versions, key=lambda v: list(map(int, v.split('.'))), default=None)
        return {
            'available': versions,
            'latest': latest_version,
            'installed': installed_version
        }

    def get_ability(self, id, version=None):
        for ability in self.abilities:
            if ability.get('id') == id and (version is None or ability.get('version') == version):
                return ability
        return None

    def retrieve_abilities(self, offset=0, limit=100, sort_by=None, sort_order='asc', filters=None, query=None):
        filtered_abilities = self._apply_filters(self.abilities, filters)
        if query:
            filtered_abilities = self._apply_query(filtered_abilities, query)
        sorted_abilities = self._apply_sorting(filtered_abilities, sort_by, sort_order)
        total_count = len(sorted_abilities)
        paginated_abilities = sorted_abilities[offset:offset + limit]
        
        return paginated_abilities, total_count

    def _apply_filters(self, abilities, filters):
        if not filters:
            return abilities
        filtered_abilities = []
        for ability in abilities:
            if all(ability.get(key) == value for key, value in filters.items()):
                filtered_abilities.append(ability)
        return filtered_abilities

    def _apply_query(self, abilities, query):
        query = query.lower()
        filtered_abilities = []
        for ability in abilities:
            if query in ability.get('id', '').lower() or query in ability.get('description', '').lower():
                filtered_abilities.append(ability)
        return filtered_abilities

    def _apply_sorting(self, abilities, sort_by, sort_order):
        if not sort_by:
            return abilities
        sorted_abilities = sorted(
            abilities,
            key=lambda x: x.get(sort_by),
            reverse=(sort_order == 'desc')
        )
        return sorted_abilities

    def refresh_abilities(self):
        self._load_abilities()

    def install_ability(self, id, version=None):
        print(f"Installing ability {id} version {version}")
        for ability in self.abilities:
            if ability['id'] == id:
                if version is None:
                    version = ability['versions']['latest']
                ability['versions']['installed'] = version
                self._set_ability_state(id, AbilityState.INSTALLING, version)
                try:
                    # TODO: Perform the installation process here

                    # If successful, set state to installed
                    self._set_ability_state(id, AbilityState.INSTALLED)
                    return True
                except Exception as e:
                    # Rollback state to available
                    self._set_ability_state(id, AbilityState.INSTALLING, rollback=True)
                    raise ValueError(f"Installation failed: {e}")
        raise ValueError("Installation failed: Ability not found")

    def uninstall_ability(self, id):
        print(f"Uninstalling ability {id}")
        for ability in self.abilities:
            if ability['id'] == id:
                self._set_ability_state(id, AbilityState.UNINSTALLING)
                try:
                    # TODO: Perform the uninstallation process here

                    # If successful, set state to available
                    self._set_ability_state(id, AbilityState.AVAILABLE)
                    ability['versions']['installed'] = None
                    return True
                except Exception as e:
                    # Rollback state to installed
                    self._set_ability_state(id, AbilityState.UNINSTALLING, rollback=True)
                    raise ValueError(f"Uninstallation failed: {e}")
        raise ValueError("Uninstallation failed: Ability not found")

    # Simple state machine using lock files to keep track of state for durability    
    def _set_ability_state(self, id, state, version=None, rollback=False):
        state_file = abilities_dir / id / state.value
        if state in [AbilityState.INSTALLING, AbilityState.UNINSTALLING]:
            if state_file.exists() and not rollback:
                raise ValueError(f"Operation failed: Another {state.value} is already in progress")
            with open(state_file, 'w') as file:
                file.write(version or state.value)
        elif state == AbilityState.INSTALLED:
            installing_file = abilities_dir / id / AbilityState.INSTALLING.value
            if installing_file.exists():
                installing_file.replace(state_file)
            else:
                raise ValueError("Operation failed: No installing file found")
        elif state == AbilityState.AVAILABLE:
            uninstalling_file = abilities_dir / id / AbilityState.UNINSTALLING.value
            if uninstalling_file.exists():
                uninstalling_file.unlink()
            else:
                raise ValueError("Operation failed: No uninstalling file found")
            
            # Remove the installed file when setting state to available
            installed_file = abilities_dir / id / AbilityState.INSTALLED.value
            if installed_file.exists():
                installed_file.unlink()
        elif rollback:
            if state == AbilityState.INSTALLING:
                (abilities_dir / id / AbilityState.INSTALLING.value).unlink(missing_ok=True)
            elif state == AbilityState.UNINSTALLING:
                (abilities_dir / id / AbilityState.UNINSTALLING.value).replace(
                    abilities_dir / id / AbilityState.INSTALLED.value
                )
