from starlette.responses import JSONResponse
from backend.managers.RagManager import RagManager
from fastapi import File, UploadFile
from typing import List


class RagIndexingView:
    def __init__(self):
        self.rm = RagManager()    

    async def post(self, resource_id: str, files: List[UploadFile] = File(...)):        
        await self.rm.upload_file(resource_id, files)        
        return JSONResponse(status_code=200, content={"message": "Document added"})