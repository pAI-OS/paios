from starlette.responses import JSONResponse, Response
from backend.managers.AssetsManager import AssetsManager
from backend.paths import api_base_url
from backend.pagination import parse_pagination_params

class AssetsView:
    def __init__(self):
        self.am = AssetsManager()

    async def get(self, id: str):
        asset = await self.am.retrieve_asset(id)
        if asset is None:
            return JSONResponse({"error": "Asset not found"}, status_code=404)
        return JSONResponse(asset, status_code=200)

    async def post(self, body: dict):
        asset_data = {
            'user_id': body.get('user_id'),
            'title': body.get('title'),
            'creator': body.get('creator'),
            'subject': body.get('subject'),
            'description': body.get('description')
        }
        id = await self.am.create_asset(**asset_data)
        asset = await self.am.retrieve_asset(id)
        return JSONResponse(asset, status_code=201, headers={'Location': f'{api_base_url}/assets/{id}'})
    
    async def put(self, id: str, body: dict):
        asset_data = {
            'user_id': body.get('user_id'),
            'title': body.get('title'),
            'creator': body.get('creator'),
            'subject': body.get('subject'),
            'description': body.get('description')
        }
        await self.am.update_asset(id, **asset_data)
        asset = await self.am.retrieve_asset(id)
        return JSONResponse(asset, status_code=200)

    async def delete(self, id: str):
        await self.am.delete_asset(id)
        return Response(status_code=204)
    
    async def search(self, filter: str = None, range: str = None, sort: str = None):
        result = parse_pagination_params(filter, range, sort)
        if isinstance(result, JSONResponse):
            return result

        offset, limit, sort_by, sort_order, filters = result

        assets, total_count = await self.am.retrieve_all_assets(limit=limit, offset=offset, sort_by=sort_by, sort_order=sort_order, filters=filters)
        headers = {
            'X-Total-Count': str(total_count),
            'Content-Range': f'assets {offset}-{offset + len(assets) - 1}/{total_count}'
        }
        return JSONResponse(assets, status_code=200, headers=headers)
