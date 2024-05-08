from flask import jsonify, request
import ChannelManager

cm = ChannelManager.ChannelManager()

def retrieve_all_channels():
    channels = cm.retrieve_all_channels()
    if channels is None:
        return jsonify({"error": "No channels found"}), 404
    return jsonify(channels), 200, {'X-Total-Count': len(channels)}

def retrieve_channel_by_id(channelId):
    channel = cm.retrieve_channel(channelId)
    if channel is None:
        return jsonify({"error": "Channel not found"}), 404
    return jsonify(channel), 200

def create_channel():
    data = request.get_json()
    cm.create_channel(data['id'], data['name'], data['uri'])
    return jsonify({"message": "Channel created successfully"}), 201

def update_channel_by_id(channelId):
    data = request.get_json()
    cm.update_channel(channelId, data['name'], data['uri'])
    return jsonify({"message": "Channel updated successfully"}), 200

def delete_channel_by_id(channelId):
    cm.delete_channel(channelId)
    return '', 204
