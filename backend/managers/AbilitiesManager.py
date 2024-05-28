import json
from pathlib import Path
from backend.paths import abilities_dir

class AbilitiesManager:
    _instance = None

    # This implementation ensures that AbilitiesManager is instantiated only once,
    # and the abilities are loaded into memory at that time.
    # You can refresh the abilities by calling AbilitiesManager().refresh_abilities()
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

    def get_all_abilities(self, limit=None):
        if limit:
            return self.abilities[:limit]
        return self.abilities

    def refresh_abilities(self):
        self._load_abilities()
