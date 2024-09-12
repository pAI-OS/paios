from starlette.responses import JSONResponse
from backend.managers.RagManager import RagManager
from backend.schemas import DocsPathsCreateSchema


class RagIndexingView:
    def __init__(self):
        self.rm = RagManager()    

    async def post(self, resource_id: str, body: DocsPathsCreateSchema):        
        await self.rm.create_index(resource_id, body)        
        return JSONResponse(status_code=200, content={"message": "Document added"})