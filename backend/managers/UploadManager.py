from typing import List
from starlette.datastructures import UploadFile
from pathlib import Path
import shutil
from .RagManager import RagManager

class UploadManager:
    async def upload_file(self, resource_id: str, files: List[UploadFile]) -> str:
        try:
            all_docs = []
            for file in files:
                # Define the directory where files will be saved
                directory = Path(f"./uploads/{resource_id}")
                directory.mkdir(parents=True, exist_ok=True)

                # Save the file
                file_path = directory / file.filename
                path = str(file_path.absolute())
                all_docs.append(path)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
            
            rm = RagManager()
            print(f"all_docs = {all_docs}")
            await rm.create_index_2(resource_id, all_docs)   
            return "Files uploaded"
        except Exception as e:
            print(f"An error occurred while uploading files: {e}")
            return "File upload failed"
