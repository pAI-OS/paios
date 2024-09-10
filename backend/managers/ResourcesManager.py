from uuid import uuid4
from threading import Lock
import httpx
from sqlalchemy import select, update, delete, func
from backend.models import Resource
from backend.db import db_session_context
from backend.schemas import ResourceCreateSchema, ResourceSchema
from typing import List, Tuple, Optional, Dict, Any

# This is a mock of the installed models in the system
ollama_model=[{'name': 'phi3:latest', 'model': 'phi3:latest', 'modified_at': '2024-08-24T21:57:16.6075173-06:00', 'size': 2176178913, 'digest': '4f222292793889a9a40a020799cfd28d53f3e01af25d48e06c5e708610fc47e9', 'details': {'parent_model': '', 'format': 'gguf', 'family': 'phi3', 'families': ['phi3'], 'parameter_size': '3.8B', 'quantization_level': 'Q4_0'}}]


class ResourcesManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ResourcesManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            with self._lock:
                if not hasattr(self, '_initialized'):
                    # db.init_db()
                    self._initialized = True
    
    async def create_resource(self, resource_data: ResourceCreateSchema) -> str:
        resource_data_table: Dict[str, Any] = {}
        kind = resource_data.get("kind")
        
        if kind == 'assistant':
            resource_data_table={  
                                "name": resource_data.get("name"), 
                                "uri": resource_data.get("uri"), 
                                "description": resource_data.get("description"),
                                "resource_llm_id": resource_data.get("resource_llm_id"),
                                "persona_id": resource_data.get("persona_id"),
                                "status": resource_data.get("status"),
                                "allow_edit": resource_data.get("allow_edit"),
                                "kind": kind
                            }
        else:
            resource_data_table={  
                                "name": resource_data.get("name"), 
                                "uri": resource_data.get("uri"), 
                                "description": resource_data.get("description"),
                                "kind": kind,
                                "icon": resource_data.get("icon")
                            }
            
        async with db_session_context() as session:
            new_resource = Resource(id=str(uuid4()), **resource_data_table)
            session.add(new_resource)
            await session.commit()
            await session.refresh(new_resource)
            return new_resource.id        
        
    async def update_resource(self, id: str, resource_data: ResourceCreateSchema) -> Optional[ResourceSchema]:
        async with db_session_context() as session:
            resource_data_table={  
                        "name": resource_data.get("name"), 
                        "uri": resource_data.get("uri"), 
                        "description": resource_data.get("description"),
                        "resource_llm_id": resource_data.get("resource_llm_id"),
                        "persona_id": resource_data.get("persona_id"),
                        "status": resource_data.get("status"),
                        "allow_edit": resource_data.get("allow_edit"),
                        "kind": resource_data.get("kind"),
                        "icon": resource_data.get("icon")
                    }
            stmt = update(Resource).where(Resource.id == id).values(**resource_data_table)
            result = await session.execute(stmt)
            if result.rowcount > 0:                
                await session.commit()
                updated_resource = await session.get(Resource, id)
                return ResourceSchema(id=updated_resource.id, **resource_data)
            return None        

    async def delete_resource(self, id: str) -> bool:
        async with db_session_context() as session:
            stmt = delete(Resource).where(Resource.id == id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0        

    async def retrieve_resource(self, id: str) -> Optional[ResourceSchema]:
        async with db_session_context() as session:
            result = await session.execute(select(Resource).filter(Resource.id == id))
            resource = result.scalar_one_or_none()
            
            if resource:
                kind = resource.kind

                if kind == 'assistant':
                    return ResourceSchema(
                        id=resource.id, 
                        name=resource.name, 
                        uri=resource.uri, 
                        description=resource.description, 
                        resource_llm_id=resource.resource_llm_id,
                        persona_id=resource.persona_id,
                        status=resource.status,
                        allow_edit=resource.allow_edit,
                        kind=resource.kind)
                else :
                    return ResourceSchema(
                        id=resource.id, 
                        name=resource.name, 
                        uri=resource.uri, 
                        description=resource.description,
                        kind=resource.kind,
                        icon=resource.icon)
            return None                    

    async def retrieve_resources(self, offset: int = 0, limit: int = 100, sort_by: Optional[str] = None, 
                                sort_order: str = 'asc', filters: Optional[Dict[str, Any]] = None) -> Tuple[List[ResourceSchema], int]:
        async with db_session_context() as session:
            query = select(Resource)

            if filters:
                for key, value in filters.items():
                    if key == 'name':
                        query = query.filter(Resource.name.ilike(f"%{value}%"))
                    if key == 'kind' and value == 'llm':
                        llm_installed = self.map_llm_to_resource(ollama_model)
                        db_llm_query = query.filter(Resource.kind == "llm")
                        result = await session.execute(db_llm_query)
                        db_llm = result.scalars().all()
                        if db_llm == []:
                            for llm in llm_installed:
                                await self.create_resource(llm)
                        query = query.filter(Resource.kind == value)
                    elif isinstance(value, list):  
                        query = query.filter(getattr(Resource, key).in_(value))
                    else:
                        query = query.filter(getattr(Resource, key) == value)

            if sort_by and sort_by in ['id', 'name', 'uri','status','allow_edit','kind']:            
                order_column = getattr(Resource, sort_by)
                query = query.order_by(order_column.desc() if sort_order.lower() == 'desc' else order_column)

            query = query.offset(offset).limit(limit)

            result = await session.execute(query)
            resources = result.scalars().all()
            
            resources = [ResourceSchema.from_orm(resource) for resource in resources]

            # Get total count
            count_query = select(func.count()).select_from(Resource)
            if filters:
                for key, value in filters.items():
                    if key == 'name':
                        count_query = count_query.filter(Resource.name.ilike(f"%{value}%"))                    
                    if isinstance(value, list):
                        count_query = count_query.filter(getattr(Resource, key).in_(value))
                    else:
                        count_query = count_query.filter(getattr(Resource, key) == value)

            total_count = await session.execute(count_query)
            total_count = total_count.scalar()

            return resources, total_count

    async def validate_resource_data(self, resource_data: ResourceCreateSchema ) -> Optional[str]:
        kind = resource_data["kind"]
        if kind not in ["llm", "assistant"]: 
            return "Not a valid kind"
        if kind == 'assistant':    
            if not resource_data.get("resource_llm_id"):
                return "It is mandatory to provide a resource_llm_id for an assistant"
            if not await self.retrieve_resource(resource_data.get("resource_llm_id")):
                return "Not a valid resource_llm_id"
        return None


    def map_llm_to_resource(self, installed_models: List[Dict]) -> List[Dict[str,Any]]:
        resources_llm = []
        for model in installed_models:
            model_field= model.get("model")
            if model_field:
                resource_llm = {                                
                                    "name": model_field,
                                    "uri":"https://ollama.com/library/"+ model_field,
                                    "description": model_field,
                                    "resource_llm_id": None,
                                    "persona_id": None,
                                    "status": None,
                                    "allow_edit": None,
                                    "kind": "llm",
                                    "icon": None
                                } 
            resources_llm.append(resource_llm)                 
        return resources_llm