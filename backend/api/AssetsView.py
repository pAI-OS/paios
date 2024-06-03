from starlette.responses import JSONResponse, Response
from backend.managers.AssetsManager import AssetsManager
from backend.paths import api_base_url

class AssetsView:
    def __init__(self):
        self.am = AssetsManager()

    async def get(self, asset_id: str):
        asset = await self.am.retrieve_asset(asset_id)
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
        asset_id = await self.am.create_asset(**asset_data)
        asset = await self.am.retrieve_asset(asset_id)
        return JSONResponse(asset, status_code=201, headers={'Location': f'{api_base_url}/assets/{asset_id}'})
    
    async def put(self, asset_id: str, body: dict):
        asset_data = {
            'user_id': body.get('user_id'),
            'title': body.get('title'),
            'creator': body.get('creator'),
            'subject': body.get('subject'),
            'description': body.get('description')
        }
        await self.am.update_asset(asset_id, **asset_data)
        asset = await self.am.retrieve_asset(asset_id)
        return JSONResponse(asset, status_code=200)

    async def delete(self, asset_id: str):
        await self.am.delete_asset(asset_id)
        return Response(status_code=204)
    
    async def search(self, limit=100):
        assets = await self.am.retrieve_all_assets(limit)
        return JSONResponse(assets, status_code=200, headers={'X-Total-Count': str(len(assets))})
    