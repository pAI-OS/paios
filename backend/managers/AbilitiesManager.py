import json
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

    def _fetch_abilities_from_directory(self):
        abilities = []
        for ability_path in abilities_dir.iterdir():
            if ability_path.is_dir():
                metadata_file = ability_path / 'metadata.json'
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        abilities.append(metadata)
        return abilities

    def get_ability(self, ability_id):
        for ability in self.abilities:
            if ability.get('id') == ability_id:
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
            match = all(ability.get(key) == value for key, value in filters.items())
            if match:
                filtered_abilities.append(ability)
        return filtered_abilities

    def _apply_query(self, abilities, query):
        query = query.lower()
        return [ability for ability in abilities if query in ability.get('title', '').lower() or query in ability.get('description', '').lower()]

    def _apply_sorting(self, abilities, sort_by, sort_order):
        if not sort_by:
            return abilities
        return sorted(abilities, key=lambda x: x.get(sort_by), reverse=(sort_order == 'desc'))

    def refresh_abilities(self):
        self._load_abilities()
