from uuid import uuid4
from threading import Lock
from sqlalchemy import select, insert, update, delete, func
from backend.models import Persona
from backend.db import db_session_context
from backend.schemas import PersonaSchema, PersonaCreateSchema
from typing import List, Tuple, Optional, Dict, Any

class PersonasManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(PersonasManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            with self._lock:
                if not hasattr(self, '_initialized'):
                    self._initialized = True

    async def create_persona(self, persona_data: PersonaCreateSchema) -> str:
        async with db_session_context() as session:
            new_persona = Persona(id=str(uuid4()), **persona_data)
            session.add(new_persona)
            await session.commit() 
            await session.refresh(new_persona)
            return new_persona.id    

    async def update_persona(self, id: str, persona_data: PersonaCreateSchema) -> Optional[PersonaSchema]:
        async with db_session_context() as session:
            stmt = update(Persona).where(Persona.id == id).values(**persona_data)
            result = await session.execute(stmt)
            if result.rowcount > 0:
                await session.commit()
                updated_persona = await session.get(Persona, id)
                return PersonaSchema(id=updated_persona.id, **persona_data)
            return None

    async def delete_persona(self, id) -> bool:
        async with db_session_context() as session:
            stmt = delete(Persona).where(Persona.id == id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    async def retrieve_persona(self, id:str) -> Optional[PersonaSchema]:
        async with db_session_context() as session:            
            result = await session.execute(select(Persona).filter(Persona.id == id))
            persona = result.scalar_one_or_none()
            if persona:
                return PersonaSchema(
                    id=persona.id,
                    name=persona.name,
                    description=persona.description,
                    voiceId=persona.voiceId,
                    faceId=persona.faceId                    
                )
            return None

    async def retrieve_personas(self, offset: int = 0, limit: int = 100, sort_by: Optional[str] = None,
                                sort_order:str = 'asc',  filters: Optional[Dict[str, Any]] = None) -> Tuple[List[PersonaSchema], int]:
        async with db_session_context() as session:
            query = select(Persona)

            if filters:
                for key, value in filters.items():
                    if key == 'name':
                        query = query.filter(Persona.name.ilike(f"%{value}%"))
                    elif isinstance(value, list):
                        query = query.filter(getattr(Persona, key).in_(value))
                    else:
                        query = query.filter(getattr(Persona, key) == value)

            if sort_by and sort_by in ['id', 'name', 'description', 'voiceId', 'faceId']:
                order_column = getattr(Persona, sort_by)
                query = query.order_by(order_column.desc() if sort_order.lower() == 'desc' else order_column)

            query = query.offset(offset).limit(limit)

            result = await session.execute(query)
            personas = [PersonaSchema.from_orm(persona) for persona in result.scalars().all()]

            # Get total count
            count_query = select(func.count()).select_from(Persona)
            if filters:
                for key, value in filters.items():
                    if key == 'name':
                        count_query = count_query.filter(Persona.name.ilike(f"%{value}%"))
                    elif isinstance(value, list):
                        count_query = count_query.filter(getattr(Persona, key).in_(value))
                    else:
                        count_query = count_query.filter(getattr(Persona, key) == value)

            total_count = await session.execute(count_query)
            total_count = total_count.scalar()

            return personas, total_count