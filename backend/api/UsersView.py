from starlette.responses import JSONResponse, Response
from common.paths import api_base_url
from backend.managers.UsersManager import UsersManager
from backend.managers.CasbinRoleManager import CasbinRoleManager
from backend.pagination import parse_pagination_params
from aiosqlite import IntegrityError
from functools import wraps
from connexion.exceptions import Forbidden
from connexion import context

def check_permission(action, resourceId="user"):
    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            cb = CasbinRoleManager()
            token_info = context.context['token_info']
            if not cb.check_permissions(token_info["role"], resourceId, action):
                raise Forbidden(description="Insufficient permissions")
        
            return await f(*args, **kwargs)
    
        return decorated_function
    return decorator

class UsersView:
    def __init__(self):
        self.um = UsersManager()

    @check_permission("show")
    async def get(self, id: str):
        user = await self.um.retrieve_user(id)
        if user is None:
            return JSONResponse(status_code=404, headers={"error": "User not found"})
        return JSONResponse(user.model_dump(), status_code=200)

    @check_permission("create")
    async def post(self, body: dict):
        try:
            id = await self.um.create_user(body['name'], body['email'])
            return JSONResponse({"id": id}, status_code=201, headers={'Location': f'{api_base_url}/users/{id}'})
        except IntegrityError:
            return JSONResponse({"message": "A user with the provided details already exists."}, status_code=400)
    
    @check_permission("edit")
    async def put(self, id: str, body: dict):
        await self.um.update_user(id, body['name'], body['email'])
        return JSONResponse({"message": "User updated successfully"}, status_code=200)

    @check_permission("delete")
    async def delete(self, id: str):
        await self.um.delete_user(id)
        return Response(status_code=204)

    @check_permission("list")
    async def search(self, filter: str = None, range: str = None, sort: str = None):
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
