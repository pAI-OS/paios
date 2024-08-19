from starlette.responses import JSONResponse, Response
from backend.managers.MessagesManager import MessagesManager
from common.paths import api_base_url
from backend.pagination import parse_pagination_params
from backend.schemas import MessageCreateSchema


class MessagesView:
    def __init__(self):
        self.mm = MessagesManager()

    async def post(self, body: MessageCreateSchema):
        id = await self.mm.create_message(body)
        message = await self.mm.retrieve_message(id)
        return JSONResponse(message.dict(), status_code=201, headers={'Location': f'{api_base_url}/messages/{id}'})