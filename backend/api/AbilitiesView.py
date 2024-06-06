from starlette.responses import JSONResponse
from backend.managers.AbilitiesManager import AbilitiesManager
from backend.pagination import parse_pagination_params

class AbilitiesView:
    def error_immutable(self):
        return JSONResponse(status_code=400, content={"message": "Invalid Request: Abilities must be installed and are immutable; their metadata.json files cannot be edited via the API."})

    async def post(self, body: dict):
        return self.error_immutable()
    
    async def put(self, body: dict):
        return self.error_immutable()
    
    async def delete(self, id: str):
        return self.error_immutable()

    def get(self, id=None):
        ability = AbilitiesManager().get_ability(id)
        if ability:
            return JSONResponse(status_code=200, content=ability)
        return JSONResponse(status_code=404, content={"message": "Ability not found"})

    async def search(self, filter: str = None, range: str = None, sort: str = None):
        result = parse_pagination_params(filter, range, sort)
        if isinstance(result, JSONResponse):
            return result

        offset, limit, sort_by, sort_order, filters = result
        query = filters.pop('q', None)

        abilities, total_count = AbilitiesManager().retrieve_abilities(
            limit=limit, 
            offset=offset, 
            sort_by=sort_by, 
            sort_order=sort_order, 
            filters=filters,
            query=query
        )
        headers = {
            'X-Total-Count': str(total_count),
            'Content-Range': f'abilities {offset}-{offset + len(abilities) - 1}/{total_count}'
        }
        return JSONResponse(abilities, status_code=200, headers=headers)

    async def install(self, id: str, version: str = None):
        manager = AbilitiesManager()
        success = manager.install_ability(id, version)
        if success:
            return JSONResponse(status_code=200, content={"message": "Ability installed"})
        return JSONResponse(status_code=404, content={"message": "Ability not found or installation failed"})
