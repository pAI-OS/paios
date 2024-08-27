from starlette.responses import JSONResponse
from backend.managers.UploadManager import UploadManager
from fastapi import UploadFile, File
from typing import List

class UploadView:
    def __init__(self):
        self.um = UploadManager()
        
    async def post(self, resource_id: str, files: List[UploadFile] = File(...)):
        for file in files:
            print("file:", file.filename)
        await self.um.upload_file(resource_id, files)
        return JSONResponse({"name": "File uploaded "}, status_code=200)
        