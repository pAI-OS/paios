from starlette.responses import JSONResponse, Response
from backend.managers.MessagesManager import MessagesManager
from common.paths import api_base_url
from backend.pagination import parse_pagination_params
from backend.schemas import MessageCreateSchema


class MessagesView:
    def __init__(self):
        self.mm = MessagesManager()

    async def post(self, body: MessageCreateSchema):
        response, error_message = await self.mm.create_message(body)
        if error_message:
            return JSONResponse({"error": error_message}, status_code=404) 
        
        if body.get("conversation_id"):  # If conversation_id was provided, retrieve the full message
            message = await self.mm.retrieve_message(response)
            return JSONResponse(message.dict(), status_code=201, headers={'Location': f'{api_base_url}/messages/{response}'})
        else:  # If conversation_id was not provided, return only the chat_response
            return JSONResponse({"chat_response": response}, status_code=200)