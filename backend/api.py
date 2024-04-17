def get_user_by_id(userId):
    users = {
        142:
            {
                "id": 142,
                "firstName": "Alice",
                "lastName": "Smith",
                "email": "alice.smith@gmail.com",
                "dateOfBirth": "1997-10-31",
                "signUpDate": "2019-08-24"
            },
        351:
            {
                "id": 351,
                "firstName": "Bob",
                "lastName": "Jones",
                "email": "bob.jones@gmail.com",
                "dateOfBirth": "1975-11-02",
                "signUpDate": "2022-10-02"
            },
    }

    user = users.get(userId)

    if user is not None:
        return user, 200  # Return the user object and a 200 OK status code
    else:
        return {"error": "User not found"}, 404  # Return an error message and a 404 Not Found status code

def not_implemented():
    return {"message": "This operation is not implemented yet."}, 501

def patch_user_by_id(userId):
    return not_implemented()

def create_new_user():
    return not_implemented()

def get_abilities_by_id(userId):
    return not_implemented()

def retrieve_all_users():
    return not_implemented()

def retrieve_all_abilities():
    return not_implemented()

def get_asset_by_id(assetId):
    return not_implemented()

def retrieve_all_assets():
    return not_implemented()
