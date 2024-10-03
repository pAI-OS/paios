from starlette.responses import JSONResponse
from backend.managers.CollectionsManager import CollectionsManager
from common.paths import api_base_url
from backend.pagination import parse_pagination_params
from backend.models import Collection
from backend.schemas import CollectionCreate  # Import from schemas.py
from typing import List

class CollectionsView:
    def __init__(self):
        self.cm = CollectionsManager()

    async def get_collection(self, id: str):
        collection = await self.cm.retrieve_collection(id)
        if collection is None:
            return JSONResponse({"error": "Collection not found"}, status_code=404)
        return JSONResponse(collection.model_dump(), status_code=200)

    async def create_collection(self, body: CollectionCreate):
        new_collection = await self.cm.create_collection(body)
        return JSONResponse(new_collection.model_dump(), status_code=201, headers={'Location': f'{api_base_url}/collections/{new_collection.id}'})
    
    async def update_collection(self, id: str, body: CollectionCreate):
        updated_collection = await self.cm.update_collection(id, body)
        if updated_collection is None:
            return JSONResponse({"error": "Collection not found"}, status_code=404)
        return JSONResponse(updated_collection.model_dump(), status_code=200)

    async def delete_collection(self, id: str):
        success = await self.cm.delete_collection(id)
        if not success:
            return JSONResponse({"error": "Collection not found"}, status_code=404)
        return Response(status_code=204)
    
    async def list_collections(self, filter: str = None, range: str = None, sort: str = None):
        result = parse_pagination_params(filter, range, sort)
        if isinstance(result, JSONResponse):
            return result

        offset, limit, sort_by, sort_order, filters = result

        # Extract the free text search query
        query = filters.pop('q', None)

        collections, total_count = await self.cm.list_collections(
            offset=offset, 
            limit=limit, 
            sort_by=sort_by, 
            sort_order=sort_order, 
            filters=filters, 
            query=query
        )
        headers = {
            'X-Total-Count': str(total_count),
            'Content-Range': f'collections {offset}-{offset + len(collections) - 1}/{total_count}'
        }
        return JSONResponse([collection.model_dump() for collection in collections], status_code=200, headers=headers)

    async def process_collection(self, id: str, body: dict):
        try:
            await self.cm.process_collection(id, body['text_splitter'], body['embedder'], body['vector_store'])
            return JSONResponse({"message": "Collection processing started"}, status_code=200)
        except ValueError as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def search_collection(self, id: str, query: str, limit: int = 10):
        try:
            results = await self.cm.search_collection(id, query, limit)
            return JSONResponse(results, status_code=200)
        except ValueError as e:
            return JSONResponse({"error": str(e)}, status_code=404)

    async def get_available_processors(self):
        processors = self.cm.get_available_processors()
        return JSONResponse(processors, status_code=200)
