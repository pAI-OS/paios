# backend/api/ConfigView.py

from starlette.responses import JSONResponse, Response
from backend.managers.ConfigManager import ConfigManager
from backend.schemas import ConfigSchema
from typing import Dict
import json

class ConfigView:
    def __init__(self):
        self.cm = ConfigManager()

    async def get(self, key: str, version: int = None, environment_id: str = None, user_id: str = None):
        config_item = await self.cm.retrieve_config_item(key, version, environment_id, user_id)
        if config_item is None:
            return JSONResponse(status_code=404, content={"error": "Config item not found"})
        return JSONResponse(config_item.model_dump(), status_code=200)

    async def put(self, key: str, body: ConfigSchema):
        updated_config = await self.cm.update_config_item(key, **body.model_dump())
        if updated_config:
            return JSONResponse(updated_config.model_dump(), status_code=200)
        return JSONResponse({"error": "Failed to update config item"}, status_code=400)

    async def delete(self, key: str, version: int = None, environment_id: str = None, user_id: str = None):
        success = await self.cm.delete_config_item(key, version, environment_id, user_id)
        if success:
            return Response(status_code=204)
        return JSONResponse({"error": "Config item not found"}, status_code=404)

    async def list(self, filter: str = None):
        filters = json.loads(filter) if filter else {}
        config_items = await self.cm.retrieve_all_config_items(filters)
        return JSONResponse([item.model_dump() for item in config_items], status_code=200)

    async def create(self, body: ConfigSchema):
        new_config = await self.cm.create_config_item(**body.model_dump())
        return JSONResponse(new_config.model_dump(), status_code=201)
