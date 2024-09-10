from starlette.responses import JSONResponse, Response
from backend.managers.ConversationsManager import ConversationsManager
from common.paths import api_base_url
from backend.pagination import parse_pagination_params
from backend.schemas import ConversationCreateSchema
 

NOT_FOUND_RESPONSE = JSONResponse({"error": "Conversation not found"}, status_code=404)
 
class ConversationsView:
    def __init__(self):
        self.cm = ConversationsManager()
 
    async def get(self, id: str):        
        conversation = await self.cm.retrieve_conversation(id)
        if conversation is None:
            return NOT_FOUND_RESPONSE
        return JSONResponse(conversation.dict(), status_code=200)
 
    async def post(self, resource_id: str, body: ConversationCreateSchema):        
        id = await self.cm.create_conversation(resource_id, body)
        conversation = await self.cm.retrieve_conversation(id)
        if conversation is None:
            return JSONResponse({"error": "Assistant not found"}, status_code=404)
        return JSONResponse(conversation.dict(), status_code=201, headers={'Location': f'{api_base_url}/conversations/{id}'})
        
    async def put(self, id: str, body: ConversationCreateSchema):
        conversation_db = await self.cm.retrieve_conversation(id)
        if conversation_db is None:
            return NOT_FOUND_RESPONSE
        await self.cm.update_conversation(id, conversation_db, body)
        conversation = await self.cm.retrieve_conversation(id)        
        return JSONResponse(conversation.dict(), status_code=200)
 
    async def delete(self, id: str):
        success = await self.cm.delete_conversation(id)
        if not success:
            return NOT_FOUND_RESPONSE
        return Response(status_code=204)
 
    async def search(self, filter: str = None, range: str = None, sort: str = None):
        result = parse_pagination_params(filter, range, sort)
        if isinstance(result, JSONResponse):
            return result
 
        offset, limit, sort_by, sort_order, filters = result
 
        conversations, total_count = await self.cm.retrieve_conversations(
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
            filters=filters
        )
        headers = {
            'X-Total-Count': str(total_count),
            'Content-Range': f'conversations {offset}-{offset + len(conversations) - 1}/{total_count}'
        }
        return JSONResponse([conversation.dict() for conversation in conversations], status_code=200, headers=headers)
