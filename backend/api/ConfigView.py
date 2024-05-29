from starlette.responses import JSONResponse, Response
from backend.managers.ConfigManager import ConfigManager

class ConfigView:
    def __init__(self):
        self.cm = ConfigManager()

    async def get(self, key: str):
        value = await self.cm.retrieve_config_item(key)
        if value is None:
            return JSONResponse(status_code=404, headers={"error": "Config item not found"})
        return JSONResponse(value, status_code=200)

    async def put(self, key: str, body: dict):
        print(f"ConfigView: PUT {key}->{body}")
        await self.cm.update_config_item(key, body)
        return JSONResponse({"message": "Config item updated successfully"}, status_code=200)

    async def delete(self, key: str):
        await self.cm.delete_config_item(key)
        return Response(status_code=204)
