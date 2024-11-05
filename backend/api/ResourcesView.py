from starlette.responses import JSONResponse, Response
from common.paths import api_base_url
from backend.managers.ResourcesManager import ResourcesManager
from backend.managers.RagManager import RagManager
from backend.managers.MessagesManager import MessagesManager
from backend.managers.ConversationsManager import ConversationsManager
from backend.pagination import parse_pagination_params
from backend.schemas import ResourceCreateSchema

class ResourcesView:
    def __init__(self):
        self.rm = ResourcesManager()

    async def get(self, id: str):
        resource = await self.rm.retrieve_resource(id)
        if resource is None:
            return JSONResponse({"error": "Resource not found"}, status_code=404)
        return JSONResponse(resource.dict(), status_code=200)

    async def post(self, body: ResourceCreateSchema):
        valid_msg = await self.rm.validate_resource_data(body)
        if valid_msg == None:
            resource_id = await self.rm.create_resource(body)
            resource = await self.rm.retrieve_resource(resource_id)
            return JSONResponse(resource.dict(), status_code=201, headers={'Location': f'{api_base_url}/resources/{resource.id}'})

        return JSONResponse({"error": " Invalid resource: " + valid_msg}, status_code=400)        

    async def put(self, id: str, body: ResourceCreateSchema):
        valid_msg = await self.rm.validate_resource_data(body)
        if valid_msg == None:
            updated_resource = await self.rm.update_resource(id, body)
        else:
            return JSONResponse({"error": " Invalid resource: " + valid_msg}, status_code=400)
        if updated_resource is None:
            return JSONResponse({"error": "Resource not found"}, status_code=404)
        return JSONResponse(updated_resource.dict(), status_code=200)        

    async def delete(self, id: str):
        ragm = RagManager()
        cm = ConversationsManager()
        msgm = MessagesManager()
        file_ids = await self.rm.retrieve_resource_files(id)
        conversations_ids = await self.rm.retrieve_resource_conversations(id)

        if file_ids:
            await ragm.delete_documents_from_chroma(id, file_ids)
            await ragm.delete_file_from_db(file_ids)     
              
        if conversations_ids:
            for conversation_id in conversations_ids:
                await cm.delete_conversation(conversation_id)
                await msgm.delete_messages_from_conversation(conversation_id)

        success_resource = await self.rm.delete_resource(id)        
        if not success_resource:
            return JSONResponse({"error": "Resource not found "}, status_code=404)
        return Response(status_code=204)

    async def search(self, filter: str = None, range: str = None, sort: str = None):
        result = parse_pagination_params(filter, range, sort)
        if isinstance(result, JSONResponse):
            return result

        offset, limit, sort_by, sort_order, filters = result

        resources, total_count = await self.rm.retrieve_resources(limit=limit, offset=offset, sort_by=sort_by, sort_order=sort_order, filters=filters)
        headers = {
            'X-Total-Count': str(total_count),
            'Content-Range': f'resources {offset}-{offset + len(resources) - 1}/{total_count}'
        }
        return JSONResponse([resource.dict() for resource in resources], status_code=200, headers=headers)

    async def shared(self, user_id: str = None):
        print("user_id: ", user_id)
        resources = await self.rm.retrieve_shared_resources(user_id)
        if resources is None:
            return JSONResponse({"error": "Shared resources not found"}, status_code=404)
        return JSONResponse([resource.dict() for resource in resources], status_code=200)

   