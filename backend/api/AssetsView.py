from starlette.responses import JSONResponse
from backend.managers.AssetsManager import AssetsManager

class AssetsView:
    def __init__(self):
        self.am = AssetsManager()

    async def get(self, assetId: str):
        asset = await self.am.retrieve_asset(assetId)
        if asset is None:
            return JSONResponse(status_code=404, headers={"error": "Asset not found"})
        return JSONResponse(asset, status_code=200)

    async def post(self, body: dict):
        asset_data = {
            'userId': body.get('userId'),
            'title': body.get('title'),
            'creator': body.get('creator'),
            'subject': body.get('subject'),
            'description': body.get('description')
        }
        asset_id = await self.am.create_asset(**asset_data)
        asset = await self.am.retrieve_asset(asset_id)
        return JSONResponse(asset, status_code=201, headers={'Location': f'/assets/{asset_id}'})
    
    async def put(self, assetId: str, body: dict):
        asset_data = {
            'userId': body.get('userId'),
            'title': body.get('title'),
            'creator': body.get('creator'),
            'subject': body.get('subject'),
            'description': body.get('description')
        }
        await self.am.update_asset(assetId, **asset_data)
        asset = await self.am.retrieve_asset(assetId)
        return JSONResponse(asset, status_code=200)

    async def delete(self, assetId: str):
        await self.am.delete_asset(assetId)
        return JSONResponse('', status_code=204)
    
    async def search(self, limit=100):
        assets = await self.am.retrieve_all_assets(limit)
        return JSONResponse(assets, status_code=200, headers={'X-Total-Count': str(len(assets))})
    