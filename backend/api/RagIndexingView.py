from starlette.responses import JSONResponse, Response
from backend.managers.RagManager import RagManager
from fastapi import File, UploadFile, Body
from typing import List
from backend.pagination import parse_pagination_params

class RagIndexingView:
    def __init__(self):
        self.rm = RagManager()
    
    async def get(self, resource_id: str):
        file = await self.rm.retrieve_file(resource_id)
        if file is None:
            return JSONResponse({"error": "File not found"}, status_code=404)
        return JSONResponse(file.dict(), status_code=200)
    
    async def post(self, resource_id: str, files: List[UploadFile] = File(...)): 
        file_info_list =  await self.rm.upload_file(resource_id, files)        
        return JSONResponse(status_code=200, content={"message": "Document added", "files": file_info_list})

    async def delete(self, resource_id: str, body: dict = Body(...)):
        file_ids = body.get("file_ids")
        success_chroma_db = await self.rm.delete_documents_from_chroma(resource_id, file_ids)
        success_db = await self.rm.delete_file_from_db(file_ids)
        if not (success_chroma_db or success_db):
            return JSONResponse({"error": "File not found"}, status_code=404)
        
        return JSONResponse(status_code=204)
    
    async def search(self, resource_id: str ,filter: str = None, range: str = None, sort: str = None):
        result = parse_pagination_params(filter, range, sort)
        if isinstance(result, JSONResponse):
            return result

        offset, limit, sort_by, sort_order, filters = result

        files, total_count = await self.rm.retrieve_files(
            resource_id=resource_id,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
            filters=filters
        )
        headers = {
            'X-Total-Count': str(total_count),
            'Content-Range': f'personas {offset}-{offset + len(files) - 1}/{total_count}'
        }
        return JSONResponse([file.dict() for file in files], status_code=200, headers=headers)