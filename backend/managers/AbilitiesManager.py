import json
import re
from backend.paths import abilities_dir

class AbilitiesManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AbilitiesManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._load_abilities()
        return cls._instance

    def _load_abilities(self):
        self.abilities = self._fetch_abilities_from_directory()
        self.installed_versions = self._load_installed_versions()

    def _fetch_abilities_from_directory(self):
        abilities = {}
        semver_pattern = re.compile(r'^\d+\.\d+\.\d+$')  # Regex for SemVer format

        for ability_path in abilities_dir.iterdir():
            if ability_path.is_dir():
                ability_name = ability_path.name
                abilities[ability_name] = {'versions': {}, 'latest': None, 'installed': None}
                for version_dir in ability_path.iterdir():
                    if version_dir.is_dir() and semver_pattern.match(version_dir.name):
                        metadata_file = version_dir / 'metadata.json'
                        if metadata_file.exists():
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                                abilities[ability_name]['versions'][version_dir.name] = metadata
                # Determine the latest version
                if abilities[ability_name]['versions']:
                    abilities[ability_name]['latest_version'] = max(
                        abilities[ability_name]['versions'].keys(), 
                        key=lambda v: list(map(int, v.split('.')))
                    )
        return abilities

    def _load_installed_versions(self):
        # Placeholder for loading installed versions from a persistent store (e.g., a file or database)
        # For now, we'll assume no versions are installed
        return {}

    def get_ability(self, id, version=None):
        for ability_name, data in self.abilities.items():
            versions = data['versions']
            if version:
                if version in versions and versions[version].get('id') == id:
                    return versions[version]
            else:
                # Return the installed version if available, otherwise the latest version
                version_to_return = self.installed_versions.get(ability_name, data['latest_version'])
                if versions[version_to_return].get('id') == id:
                    return versions[version_to_return]
        return None

    def retrieve_abilities(self, offset=0, limit=100, sort_by=None, sort_order='asc', filters=None, query=None):
        filtered_abilities = self._apply_filters(self.abilities, filters)
        if query:
            filtered_abilities = self._apply_query(filtered_abilities, query)
        sorted_abilities = self._apply_sorting(filtered_abilities, sort_by, sort_order)
        total_count = len(sorted_abilities)
        paginated_abilities = list(sorted_abilities.items())[offset:offset + limit]
        
        # Convert the paginated abilities to the expected format
        abilities_list = []
        for ability_name, data in paginated_abilities:
            latest_version = data['latest_version']
            ability_info = data['versions'][latest_version]
            ability_info['latest_version'] = latest_version
            ability_info['installed_version'] = self.installed_versions.get(ability_name)
            abilities_list.append(ability_info)
        
        return abilities_list, total_count

    def _apply_filters(self, abilities, filters):
        if not filters:
            return abilities
        filtered_abilities = {}
        for ability_name, data in abilities.items():
            match = all(data.get(key) == value for key, value in filters.items())
            if match:
                filtered_abilities[ability_name] = data
        return filtered_abilities

    def _apply_query(self, abilities, query):
        query = query.lower()
        filtered_abilities = {}
        for ability_name, data in abilities.items():
            for version, metadata in data['versions'].items():
                if query in metadata.get('name', '').lower() or query in metadata.get('description', '').lower():
                    filtered_abilities[ability_name] = data
                    break
        return filtered_abilities

    def _apply_sorting(self, abilities, sort_by, sort_order):
        if not sort_by:
            return abilities
        sorted_abilities = sorted(
            abilities.items(),
            key=lambda x: x[1]['versions'][x[1]['latest_version']].get(sort_by),
            reverse=(sort_order == 'desc')
        )
        return dict(sorted_abilities)

    def refresh_abilities(self):
        self._load_abilities()

    def install_ability(self, ability_name, version):
        # Logic to install the ability
        # Update the installed version in the abilities data structure
        if ability_name in self.abilities and version in self.abilities[ability_name]['versions']:
            self.installed_versions[ability_name] = version
            # Persist this information as needed

    def get_installed_version(self, ability_name):
        return self.installed_versions.get(ability_name)

    def get_latest_version(self, ability_name):
        return self.abilities.get(ability_name, {}).get('latest_version')
