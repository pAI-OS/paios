from starlette.responses import JSONResponse
from backend.managers.EnvironmentsManager import EnvironmentsManager
from backend.schemas import EnvironmentCreateSchema, EnvironmentSchema

class EnvironmentsView:
    def __init__(self):
        self.em = EnvironmentsManager()

    async def get(self, environment_id: str):
        environment = await self.em.retrieve_environment(environment_id)
        if environment is None:
            return JSONResponse({"error": "Environment not found"}, status_code=404)
        return JSONResponse(environment, status_code=200)

    async def post(self, body: EnvironmentCreateSchema):
        try:
            new_environment = await self.em.create_environment(body.dict())
            return JSONResponse(new_environment, status_code=201)
        except ValueError as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def put(self, environment_id: str, body: EnvironmentCreateSchema):
        try:
            updated_environment = await self.em.update_environment(environment_id, body.dict())
            if updated_environment is None:
                return JSONResponse({"error": "Environment not found"}, status_code=404)
            return JSONResponse(updated_environment, status_code=200)
        except ValueError as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def delete(self, environment_id: str):
        try:
            success = await self.em.delete_environment(environment_id)
            if not success:
                return JSONResponse({"error": "Environment not found"}, status_code=404)
            return JSONResponse(status_code=204)
        except ValueError as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def search(self):
        environments = await self.em.retrieve_environments()
        return JSONResponse(environments, status_code=200)
