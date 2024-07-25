from starlette.responses import JSONResponse, Response
from common.paths import api_base_url
from backend.managers.ChannelsManager import ChannelsManager
from backend.pagination import parse_pagination_params
from backend.schemas import ChannelCreateSchema
from typing import List

class ChannelsView:
    def __init__(self):
        self.cm = ChannelsManager()

    async def get(self, id: str):
        channel = await self.cm.retrieve_channel(id)
        if channel is None:
            return JSONResponse({"error": "Channel not found"}, status_code=404)
        return JSONResponse(channel.dict(), status_code=200)

    async def post(self, body: ChannelCreateSchema):
        valid_msg = self.cm.validate_channel_data(body)
        if valid_msg == None:
            assistant_id = await self.cm.create_channel(body)
            files = body["files"]
            for file_name in files:
                await self.cm.create_file(file_name, assistant_id)
            channel = await self.cm.retrieve_channel(assistant_id)
            return JSONResponse(channel.dict(), status_code=201, headers={'Location': f'{api_base_url}/channels/{channel.id}'})

        return JSONResponse({"error": " Invalid channel: " + valid_msg}, status_code=400)

    async def put(self, id: str, body: ChannelCreateSchema):
        valid_msg = self.cm.validate_channel_data(body)
        if valid_msg == None:
            updated_channel = await self.cm.update_channel(id, body)
        else:
            return JSONResponse({"error": " Invalid channel: " + valid_msg}, status_code=400)
        if updated_channel is None:
            return JSONResponse({"error": "Channel not found"}, status_code=404)
        return JSONResponse(updated_channel.dict(), status_code=200)

    async def delete(self, id: str):
        success = await self.cm.delete_channel(id)
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
        return JSONResponse([channel.dict() for channel in channels], status_code=200, headers=headers)
