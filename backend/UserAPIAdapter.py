from uuid import uuid4
from flask import jsonify, request
import UserManager

um = UserManager.UserManager()

def retrieve_all_users():
    users = um.retrieve_all_users()
    return jsonify(users), 200, {'X-Total-Count': len(users)}

def retrieve_user_by_id(userId):
    user = um.retrieve_user(userId)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200

def create_user():
    user = request.get_json()
    user['id'] = um.create_user(user['name'], user['email'])
    # TODO: Return 409 if email already exists?
    return jsonify(user), 201, {'Location': f'/users/{user["id"]}'}

def update_user_by_id(userId):
    data = request.get_json()
    um.update_user(userId, data.get('name'), data.get('email'))
    return jsonify({"message": "User updated successfully"}), 200

def delete_user_by_id(userId):
    um.delete_user(userId)
    return '', 204
