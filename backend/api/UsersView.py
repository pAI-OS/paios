from starlette.responses import JSONResponse
from backend.managers.UserManager import UserManager

class UsersView:
    def __init__(self):
        self.um = UserManager()

    async def get(self, userId: str):
        user = await self.um.retrieve_user(userId)
        if user is None:
            return JSONResponse(status_code=404, headers={"error": "User not found"})
        return JSONResponse(user, status_code=200)

    async def post(self, body: dict):
        user_id = await self.um.create_user(body['name'], body['email'])
        return JSONResponse({"id": user_id}, status_code=201, headers={'Location': f'/users/{user_id}'})
    
    async def put(self, userId: str, body: dict):
        await self.um.update_user(userId, body['name'], body['email'])
        return JSONResponse({"message": "User updated successfully"}, status_code=200)

    async def delete(self, userId: str):
        await self.um.delete_user(userId)
        return JSONResponse('', status_code=204)
    
    async def search(self, limit=100):
        users = await self.um.retrieve_all_users(limit)
        return JSONResponse(users, status_code=200, headers={'X-Total-Count': str(len(users))})
