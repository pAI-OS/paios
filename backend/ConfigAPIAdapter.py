# config_api_adapter.py
import json
from flask import jsonify
import ConfigManager

class ConfigAPIAdapter:
    def __init__(self):
        self.cm = ConfigManager.ConfigManager()

    def retrieve_config_by_key(self, key):
        value = self.cm.retrieve_config_item(key)
        if value is None:
            return jsonify({"error": "Config item not found"}), 404
        return jsonify(value), 200

    def update_config_by_key(self, key, body):
        self.cm.update_config_item(key, json.dumps(body))
        return jsonify({"message": "Config item updated successfully"}), 200

    def delete_config_by_key(self, key):
        self.cm.delete_config_item(key)
        return '', 204

# factory
def create_adapter():
    return ConfigAPIAdapter()
