from starlette.responses import JSONResponse, Response
from backend.managers.ChannelsManager import ChannelsManager
from backend.paths import api_base_url
from backend.pagination import parse_pagination_params

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

    async def search(self, filter: str = None, range: str = None, sort: str = None):
        result = parse_pagination_params(filter, range, sort)
        if isinstance(result, JSONResponse):
            return result

        offset, limit, sort_by, sort_order, filters = result

        channels, total_count = await self.cm.retrieve_channels(limit=limit, offset=offset, sort_by=sort_by, sort_order=sort_order, filters=filters)
        headers = {
            'X-Total-Count': str(total_count),
            'Content-Range': f'channels {offset}-{offset + len(channels) - 1}/{total_count}'
        }
        return JSONResponse(channels, status_code=200, headers=headers)
