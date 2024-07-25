from starlette.responses import JSONResponse, Response
from common.paths import api_base_url
from backend.managers.ChannelsManager import ChannelsManager
from backend.pagination import parse_pagination_params
from backend.schemas import ChannelCreateSchema
from typing import List

class ChannelsView:
    def __init__(self):
        self.cm = ChannelsManager()

    async def get(self, channel_id: str):
        channel = await self.cm.retrieve_channel(channel_id)
        if channel is None:
            return JSONResponse({"error": "Channel not found"}, status_code=404)
        return JSONResponse(channel.model_dump(), status_code=200)

    async def post(self, body: ChannelCreateSchema):
        new_channel = await self.cm.create_channel(body)
        return JSONResponse(new_channel.model_dump(), status_code=201, headers={'Location': f'{api_base_url}/channels/{new_channel.id}'})

    async def put(self, channel_id: str, body: ChannelCreateSchema):
        updated_channel = await self.cm.update_channel(channel_id, body)
        if updated_channel is None:
            return JSONResponse({"error": "Channel not found"}, status_code=404)
        return JSONResponse(updated_channel.model_dump(), status_code=200)

    async def delete(self, channel_id: str):
        success = await self.cm.delete_channel(channel_id)
        if not success:
            return JSONResponse({"error": "Channel not found"}, status_code=404)
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
        return JSONResponse([channel.model_dump() for channel in channels], status_code=200, headers=headers)
