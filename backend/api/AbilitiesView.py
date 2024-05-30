from starlette.responses import JSONResponse
from backend.managers.AbilitiesManager import AbilitiesManager

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

    def search(self, limit=100):
        abilities = AbilitiesManager().get_all_abilities(limit)
        return JSONResponse(status_code=200, content=abilities, headers={'X-Total-Count': str(len(abilities))})
