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
    
    async def delete(self, ability_id: str):
        return self.error_immutable()

    def get(self, ability_id=None):
        return JSONResponse(status_code=200, content=AbilitiesManager().get_ability(ability_id))

    async def search(self, filter: str = None, range: str = None, sort: str = None):
        result = parse_pagination_params(filter, range, sort)
        if isinstance(result, JSONResponse):
            return result

        offset, limit, sort_by, sort_order, filters = result

        abilities, total_count = AbilitiesManager().retrieve_abilities(limit=limit, offset=offset)
        headers = {
            'X-Total-Count': str(total_count),
            'Content-Range': f'abilities {offset}-{offset + len(abilities) - 1}/{total_count}'
        }
        return JSONResponse(abilities, status_code=200, headers=headers)
