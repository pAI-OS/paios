from starlette.responses import JSONResponse, Response
from backend.managers.ConfigManager import ConfigManager
from backend.schemas import ConfigSchema

class ConfigView:
    def __init__(self):
        self.cm = ConfigManager()

    async def get(self, key: str):
        config_item = await self.cm.retrieve_config_item(key)
        if config_item is None:
            return JSONResponse(status_code=404, content={"error": "Config item not found"})
        return JSONResponse(config_item.model_dump(), status_code=200)

    async def put(self, key: str, body: ConfigSchema):
        print(f"ConfigView: PUT {key}->{body}")
        updated_config = await self.cm.update_config_item(key, body.value)
        if updated_config:
            return JSONResponse(updated_config.model_dump(), status_code=200)
        return JSONResponse({"error": "Failed to update config item"}, status_code=400)

    async def delete(self, key: str):
        success = await self.cm.delete_config_item(key)
        if success:
            return Response(status_code=204)
        return JSONResponse({"error": "Config item not found"}, status_code=404)

    async def list(self):
        config_items = await self.cm.retrieve_all_config_items()
        return JSONResponse([item.model_dump() for item in config_items], status_code=200)

    async def create(self, body: ConfigSchema):
        new_config = await self.cm.create_config_item(body.value)
        return JSONResponse(new_config.model_dump(), status_code=201)
