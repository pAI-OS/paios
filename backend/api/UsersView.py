from starlette.responses import JSONResponse, Response
from common.paths import api_base_url
from backend.managers.UsersManager import UsersManager
from backend.managers.CasbinRoleManager import CasbinRoleManager
from backend.pagination import parse_pagination_params
from aiosqlite import IntegrityError
from backend.schemas import UserSchema

class UsersView:
    def __init__(self):
        self.um = UsersManager()
        self.cb = CasbinRoleManager()

    async def get(self, token_info, id: str):
        if not self.cb.check_permissions(token_info["role"], 'user', 'show'):
            return JSONResponse({"message": "Permission denied"}, status_code=403)
        
        user = await self.um.retrieve_user(id)
        if user is None:
            return JSONResponse(status_code=404, headers={"error": "User not found"})
        return JSONResponse(user.model_dump(), status_code=200)

    async def post(self,token_info, body: dict):
        if not self.cb.check_permissions(token_info["role"], 'user', 'create'):
            return JSONResponse({"message": "Permission denied"}, status_code=403)
        try:
            id = await self.um.create_user(body['name'], body['email'])
            return JSONResponse({"id": id}, status_code=201, headers={'Location': f'{api_base_url}/users/{id}'})
        except IntegrityError:
            return JSONResponse({"message": "A user with the provided details already exists."}, status_code=400)
    
    async def put(self, token_info, id: str, body: dict):
        if not self.cb.check_permissions(token_info["role"], 'user', 'edit'):
            return JSONResponse({"message": "Permission denied"}, status_code=403)
        
        await self.um.update_user(id, body['name'], body['email'])
        return JSONResponse({"message": "User updated successfully"}, status_code=200)

    async def delete(self, token_info, id: str):
        if not self.cb.check_permissions(token_info["role"], 'user', 'delete'):
            return JSONResponse({"message": "Permission denied"}, status_code=403)
        await self.um.delete_user(id)
        return Response(status_code=204)

    async def search(self, token_info, filter: str = None, range: str = None, sort: str = None):
        if not self.cb.check_permissions(token_info["role"], 'user', 'list'):
            return JSONResponse({"message": "Permission denied"}, status_code=403)
        result = parse_pagination_params(filter, range, sort)
        if isinstance(result, JSONResponse):
            return result

        offset, limit, sort_by, sort_order, filters = result

        users, total_count = await self.um.retrieve_users(limit=limit, offset=offset, sort_by=sort_by, sort_order=sort_order, filters=filters)
        
        # Convert Pydantic models to dictionaries
        users_dict = [user.model_dump() for user in users]
        
        headers = {
            'X-Total-Count': str(total_count),
            'Content-Range': f'users {offset}-{offset+len(users)}/{total_count}',
            'Access-Control-Expose-Headers': 'Content-Range'
        }
        return JSONResponse(users_dict, status_code=200, headers=headers)
