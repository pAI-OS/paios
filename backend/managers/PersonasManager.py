from uuid import uuid4
import backend.db as db
from backend.utils import remove_null_fields, zip_fields
from threading import Lock
import logging

logger = logging.getLogger(__name__)

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
                    db.init_db()
                    self._initialized = True

    async def create_persona(self, name, description, voiceId, faceId):
        id = str(uuid4())
        query = 'INSERT INTO persona (id, name, description, voiceId, faceId) VALUES (?, ?, ?, ?, ?)'
        await db.execute_query(query, (id, name, description, voiceId, faceId))
        return id

    async def update_persona(self, id, name, description, voiceId, faceId):
        query = 'INSERT OR REPLACE INTO persona (id, name, description, voiceId, faceId) VALUES (?, ?, ?, ?, ?)'
        return await db.execute_query(query, (id, name, description, voiceId, faceId))

    async def delete_persona(self, id):
        query = 'DELETE FROM persona WHERE id = ?'
        return await db.execute_query(query, (id,))

    async def retrieve_persona(self, id):
        query = 'SELECT id, name, description, voiceId, faceId FROM persona WHERE id = ?'
        result = await db.execute_query(query, (id,))
        if result:
            fields = ['id', 'name', 'description', 'voiceId', 'faceId']
            persona = remove_null_fields(zip_fields(fields, result[0]))
            persona['id'] = id
            return persona
        return None

    async def retrieve_personas(self, offset=0, limit=100, sort_by=None, sort_order='asc', filters=None):
        # Initialize filters to an empty dictionary if it is None
        if filters is None:
            filters = {}

        base_query = 'SELECT id, name, description, voiceId, faceId FROM persona'
        query_params = []

        # Apply filters
        filter_clauses = []
        if filters:
            for key, value in filters.items():
                if key == 'name':
                    filter_clauses.append(f"LOWER(name) LIKE ?")
                    query_params.append(f"%{value.lower()}%")
                else:
                    if isinstance(value, list):
                        placeholders = ', '.join(['?'] * len(value))
                        filter_clauses.append(f"{key} IN ({placeholders})")
                        query_params.extend(value)
                    else:
                        filter_clauses.append(f"{key} = ?")
                        query_params.append(value)

        if filter_clauses:
            base_query += ' WHERE ' + ' AND '.join(filter_clauses)

        # Validate and apply sorting
        valid_sort_columns = ['id', 'name', 'description', 'voiceId', 'faceId']
        if sort_by and sort_by in valid_sort_columns:
            sort_order = 'DESC' if sort_order.lower() == 'desc' else 'ASC'
            base_query += f' ORDER BY {sort_by} {sort_order}'

        # Apply pagination
        base_query += ' LIMIT ? OFFSET ?'
        query_params.extend([limit, offset])

        # Execute the main query
        logger.info("base_query = %s", base_query)
        logger.info("query_params = %s", query_params)
        results = await db.execute_query(base_query, tuple(query_params))
        
        fields = ['id', 'name', 'description', 'voiceId', 'faceId']
        personas = [remove_null_fields(zip_fields(fields, result)) for result in results]

        # Get the total count of personas
        total_count_query = 'SELECT COUNT(*) FROM persona'
        total_count_params = query_params[:-2]  # Exclude limit and offset for the count query
        if filter_clauses:
            total_count_query += ' WHERE ' + ' AND '.join(filter_clauses)
        total_count_result = await db.execute_query(total_count_query, tuple(total_count_params))
        total_count = total_count_result[0][0] if total_count_result else 0

        return personas, total_count
