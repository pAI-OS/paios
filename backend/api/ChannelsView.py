from starlette.responses import JSONResponse, Response
from backend.managers.ChannelsManager import ChannelsManager
from backend.paths import api_base_url

class ChannelsView:
    def __init__(self):
        self.cm = ChannelsManager()

    async def get(self, channel_id: str):
        channel = await self.cm.retrieve_channel(channel_id)
        if channel is None:
            return JSONResponse({"error": "Channel not found"}, status_code=404)
        return JSONResponse(channel, status_code=200)

    async def post(self, body: dict):
        channel_id = await self.cm.create_channel(body['name'], body['uri'])
        return JSONResponse({"id": channel_id}, status_code=201, headers={'Location': f'{api_base_url}/channels/{channel_id}'})

    async def put(self, channel_id: str, body: dict):
        await self.cm.update_channel(channel_id, body['name'], body['uri'])
        return JSONResponse({"message": "Channel updated successfully"}, status_code=200)

    async def delete(self, channel_id: str):
        await self.cm.delete_channel(channel_id)
        return Response(status_code=204)

    async def search(self, limit=100):
        channels = await self.cm.retrieve_all_channels(limit)
        return JSONResponse(channels, status_code=200, headers={'X-Total-Count': str(len(channels))})
    