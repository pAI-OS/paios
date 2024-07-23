from starlette.responses import JSONResponse, Response
from backend.managers.AssetsManager import AssetsManager
from common.paths import api_base_url
from backend.pagination import parse_pagination_params
from backend.schemas import AssetCreateSchema, AssetSchema
from typing import List

class AssetsView:
    def __init__(self):
        self.am = AssetsManager()

    async def get(self, id: str):
        asset = await self.am.retrieve_asset(id)
        if asset is None:
            return JSONResponse({"error": "Asset not found"}, status_code=404)
        return JSONResponse(asset.model_dump(), status_code=200)

    async def post(self, body: AssetCreateSchema):
        new_asset = await self.am.create_asset(body)
        return JSONResponse(new_asset.model_dump(), status_code=201, headers={'Location': f'{api_base_url}/assets/{new_asset.id}'})
    
    async def put(self, id: str, body: AssetCreateSchema):
        updated_asset = await self.am.update_asset(id, body)
        if updated_asset is None:
            return JSONResponse({"error": "Asset not found"}, status_code=404)
        return JSONResponse(updated_asset.model_dump(), status_code=200)

    async def delete(self, id: str):
        success = await self.am.delete_asset(id)
        if not success:
            return JSONResponse({"error": "Asset not found"}, status_code=404)
        return Response(status_code=204)
    
    async def search(self, filter: str = None, range: str = None, sort: str = None):
        result = parse_pagination_params(filter, range, sort)
        if isinstance(result, JSONResponse):
            return result

        offset, limit, sort_by, sort_order, filters = result

        # Extract the free text search query
        query = filters.pop('q', None)

        assets, total_count = await self.am.retrieve_assets(
            limit=limit, 
            offset=offset, 
            sort_by=sort_by, 
            sort_order=sort_order, 
            filters=filters, 
            query=query
        )
        headers = {
            'X-Total-Count': str(total_count),
            'Content-Range': f'assets {offset}-{offset + len(assets) - 1}/{total_count}'
        }
        return JSONResponse([asset.model_dump() for asset in assets], status_code=200, headers=headers)
