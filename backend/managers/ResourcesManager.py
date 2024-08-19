from uuid import uuid4
from threading import Lock
from sqlalchemy import select, insert, update, delete, func
from backend.models import Resource, File
from backend.db import db_session_context
from backend.schemas import ResourceCreateSchema, ResourceSchema
from typing import List, Tuple, Optional, Dict, Any

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
            
            # Set files for the resource
            if kind == 'assistant' and resource_data.get("files"):
                self.create_files_for_resource(new_resource.id, resource_data["files"])
            return new_resource.id        
    
    async def create_files_for_resource(self, resource_id: str, files: List[str]):
        for file_name in files:
            await self.create_file(file_name, resource_id)
        
    async def update_resource(self, id: str, resource_data: ResourceCreateSchema) -> Optional[ResourceSchema]:
        async with db_session_context() as session:
            resource_data_table={  
                        "name": resource_data["name"], 
                        "uri": resource_data["uri"], 
                        "description": resource_data["description"],
                        "resource_llm_id": resource_data["resource_llm_id"],
                        "persona_id": resource_data["persona_id"],
                        "status": resource_data["status"],
                        "allow_edit": resource_data["allow_edit"],
                        "kind": resource_data["kind"],
                        "icon": resource_data["icon"]
                    }
            files = resource_data["files"]

            for file in files:
                self.update_file(id, file)
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
            files_result = await session.execute(select(File).filter(File.assistant_id == id))
            files = [file.name for file in files_result.scalars()]
            resource = result.scalar_one_or_none()
            
            kind = resource.kind
            if resource:
                if kind == 'assistant':
                    return ResourceSchema(
                        id=resource.id, 
                        name=resource.name, 
                        uri=resource.uri, 
                        description=resource.description, 
                        resource_llm_id=resource.resource_llm_id,
                        persona_id=resource.persona_id,
                        files=files,
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
            for resource in resources:
                files_result = await session.execute(select(File).filter(File.assistant_id == resource.id))
                files = [file.name for file in files_result.scalars()]
                resource.files = files

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
        
    async def create_file(self, file_name: str, assistant_id: str ) -> str:        
        async with db_session_context() as session:
            new_file = File(id=str(uuid4()), name=file_name, assistant_id=assistant_id)
            session.add(new_file)
            await session.commit()
            await session.refresh(new_file)
            return new_file.id

    async def update_file(self, assistant_id: str, file_name: str) -> str:
        async with db_session_context() as session:
            # delete the file from the database if it exists
            stmt = delete(File).where(File.assistant_id == assistant_id)
            await session.execute(stmt)
            await session.commit()
            return self.create_file(file_name, assistant_id)

    def validate_resource_data(self, resource_data: ResourceCreateSchema ) -> str:
        kind = resource_data["kind"]
        if not kind in ["llm", "assistant"]:
            return "Not a valid kind"
        if kind == 'assistant':    
            if not resource_data["resource_llm_id"]:
                return "Not a valid resource_llm_id"
        return None
