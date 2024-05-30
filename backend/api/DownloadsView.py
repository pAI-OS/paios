from starlette.requests import Request
from starlette.responses import JSONResponse
from backend.managers.DownloadsManager import DownloadsManager
from backend.paths import api_base_url

class DownloadsView:
    def __init__(self):
        self.manager = DownloadsManager()

    async def get(self):
        downloads = await self.manager.retrieve_all_downloads()
        return JSONResponse(status_code=200, content=downloads)

    async def post(self, body: dict):
        source_url = body.get('source_url')
        target_file = body.get('target_file')
        target_dir = body.get('target_dir', 'downloads')
        hash_type = body.get('hash_type')
        expected_hash = body.get('expected_hash')
        
        if not source_url:
            return JSONResponse(status_code=400, content={"message": "Invalid request: 'source_url' is required"})
        
        try:
            download_id = await self.manager.start_download(
                source_url, target_file=target_file, target_dir=target_dir, 
                hash_type=hash_type, expected_hash=expected_hash
            )
            return JSONResponse(status_code=200, content={"id": download_id}, headers={'Location': f'{api_base_url}/downloads/{download_id}'})
        except Exception as e:
            return JSONResponse(status_code=400, content={"message": str(e)})

    async def put(self):
        return JSONResponse(status_code=501, content={"message": "Not Implemented"})

    async def delete(self, id: str):
        await self.manager.delete_download(id)
        return JSONResponse(status_code=204)

    async def search(self, limit=100):
        downloads = await self.manager.retrieve_all_downloads(limit)
        return JSONResponse(status_code=200, content=downloads, headers={'X-Total-Count': str(len(downloads))})

# custom functions

    async def pause(self, download_id: str):
        self.manager.pause_download(download_id)
        return JSONResponse(status_code=200, content={"message": "Download paused"})

    async def resume(self, download_id: str):
        await self.manager.resume_download(download_id)
        return JSONResponse(status_code=200, content={"message": "Download resumed"})
