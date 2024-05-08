from flask import jsonify, request
import UserManager

um = UserManager.UserManager()

def retrieve_all_users():
    users = um.retrieve_all_users()
    return jsonify(users), 200, {'X-Total-Count': len(users)}

def retrieve_user_by_id(user_id):
    user = um.retrieve_user(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200

def create_user():
    data = request.get_json()
    um.create_user(data['name'], data['email'])
    return jsonify({"message": "User created successfully"}), 201

def update_user_by_id(user_id):
    data = request.get_json()
    um.update_user(user_id, data.get('name'), data.get('email'))
    return jsonify({"message": "User updated successfully"}), 200

def delete_user_by_id(user_id):
    um.delete_user(user_id)
    return '', 204
