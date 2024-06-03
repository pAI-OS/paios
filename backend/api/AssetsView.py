from starlette.responses import JSONResponse, Response
from backend.managers.AssetsManager import AssetsManager
from backend.paths import api_base_url

class AssetsView:
    def __init__(self):
        self.am = AssetsManager()

    async def get(self, id: str):
        asset = await self.am.retrieve_asset(id)
        if asset is None:
            return JSONResponse({"error": "Asset not found"},status_code=404)
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
    
    async def search(self, limit=100):
        assets = await self.am.retrieve_all_assets(limit)
        return JSONResponse(assets, status_code=200, headers={'X-Total-Count': str(len(assets))})
    