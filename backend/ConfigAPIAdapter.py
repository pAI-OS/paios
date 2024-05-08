# ConfigAPIAdapter.py
import json
from flask import jsonify
import ConfigManager

cm = ConfigManager.ConfigManager()

def retrieve_config_by_key(key):
    value = cm.retrieve_config_item(key)
    if value is None:
        return jsonify({"error": "Config item not found"}), 404
    if isinstance(value, str):
        try:
            value = json.loads(value)  # Convert string back to dict if necessary
        except json.JSONDecodeError:
            pass  # It's a plain string, not JSON
    return jsonify(value), 200

def update_config_by_key(key, body):
    cm.update_config_item(key, json.dumps(body))
    return jsonify({"message": "Config item updated successfully"}), 200

def delete_config_by_key(key):
    cm.delete_config_item(key)
    return '', 204
