from starlette.responses import JSONResponse, Response
from common.paths import api_base_url
from backend.managers.ResourcesManager import ResourcesManager
from backend.pagination import parse_pagination_params
from backend.schemas import ChannelCreateSchema
from typing import List

class ResourcesView:
    def __init__(self):
        self.cm = ResourcesManager()

    async def get(self, resource_id: str):
        resource = await self.cm.retrieve_resource(resource_id)
        if resource is None:
            return JSONResponse({"error": "Resource not found"}, status_code=404)
        return JSONResponse(resource.model_dump(), status_code=200)

    async def post(self, body: ChannelCreateSchema):
        new_resource = await self.cm.create_resource(body)
        return JSONResponse(new_resource.model_dump(), status_code=201, headers={'Location': f'{api_base_url}/resources/{new_resource.id}'})

    async def put(self, resource_id: str, body: ChannelCreateSchema):
        updated_resource = await self.cm.update_resource(resource_id, body)
        if updated_resource is None:
            return JSONResponse({"error": "Resource not found"}, status_code=404)
        return JSONResponse(updated_resource.model_dump(), status_code=200)

    async def delete(self, resource_id: str):
        success = await self.cm.delete_resource(resource_id)
        if not success:
            return JSONResponse({"error": "Resource not found"}, status_code=404)
        return Response(status_code=204)

    async def search(self, filter: str = None, range: str = None, sort: str = None):
        result = parse_pagination_params(filter, range, sort)
        if isinstance(result, JSONResponse):
            return result

        offset, limit, sort_by, sort_order, filters = result

        resources, total_count = await self.cm.retrieve_resources(limit=limit, offset=offset, sort_by=sort_by, sort_order=sort_order, filters=filters)
        headers = {
            'X-Total-Count': str(total_count),
            'Content-Range': f'resources {offset}-{offset + len(resources) - 1}/{total_count}'
        }
        return JSONResponse([resource.model_dump() for resource in resources], status_code=200, headers=headers)
