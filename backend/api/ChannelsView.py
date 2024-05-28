from starlette.responses import JSONResponse
from backend.managers.ChannelManager import ChannelManager

class ChannelsView:
    def __init__(self):
        self.cm = ChannelManager()

    async def get(self, channelId: str):
        channel = await self.cm.retrieve_channel(channelId)
        if channel is None:
            return JSONResponse({"error": "Channel not found"}, status_code=404)
        return JSONResponse(channel, status_code=200)

    async def post(self, body: dict):
        channel_id = await self.cm.create_channel(body['name'], body['uri'])
        return JSONResponse({"id": channel_id}, status_code=201, headers={'Location': f'/channels/{channel_id}'})

    async def put(self, channelId: str, body: dict):
        await self.cm.update_channel(channelId, body['name'], body['uri'])
        return JSONResponse({"message": "Channel updated successfully"}, status_code=200)

    async def delete(self, channelId: str):
        await self.cm.delete_channel(channelId)
        return JSONResponse('', status_code=204)

    async def search(self, limit=100):
        channels = await self.cm.retrieve_all_channels(limit)
        return JSONResponse(channels, status_code=200, headers={'X-Total-Count': str(len(channels))})