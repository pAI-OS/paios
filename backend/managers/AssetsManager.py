from uuid import uuid4
import backend.db as db
from backend.utils import remove_null_fields, zip_fields
from threading import Lock

class AssetsManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(AssetsManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            with self._lock:
                if not hasattr(self, '_initialized'):
                    db.init_db()
                    self._initialized = True

    async def create_asset(self, user_id, title, creator, subject, description):
        id = str(uuid4())
        query = 'INSERT INTO asset (id, user_id, title, creator, subject, description) VALUES (?, ?, ?, ?, ?, ?)'
        await db.execute_query(query, (id, user_id, title, creator, subject, description))
        return id

    async def update_asset(self, id, user_id, title, creator, subject, description):
        query = 'INSERT OR REPLACE INTO asset (id, user_id, title, creator, subject, description) VALUES (?, ?, ?, ?, ?, ?)'
        return await db.execute_query(query, (id, user_id, title, creator, subject, description))

    async def delete_asset(self, id):
        query = 'DELETE FROM asset WHERE id = ?'
        return await db.execute_query(query, (id,))

    async def retrieve_asset(self, id):
        query = 'SELECT user_id, title, creator, subject, description FROM asset WHERE id = ?'
        result = await db.execute_query(query, (id,))
        if result:
            fields = ['user_id', 'title', 'creator', 'subject', 'description']
            asset = remove_null_fields(zip_fields(fields, result[0]))
            asset['id'] = id
            return asset
        return None

    async def retrieve_assets(self, offset=0, limit=100, sort_by=None, sort_order='asc', filters=None, query=None):
        base_query = 'SELECT id, user_id, title, creator, subject, description FROM asset'
        query_params = []

        # Apply filters
        filter_clauses = []
        if filters:
            for key, value in filters.items():
                if isinstance(value, list):
                    placeholders = ', '.join(['?'] * len(value))
                    filter_clauses.append(f"{key} IN ({placeholders})")
                    query_params.extend(value)
                else:
                    filter_clauses.append(f"{key} = ?")
                    query_params.append(value)

        # Apply free text search
        if query:
            query_clause = "(title LIKE ? OR description LIKE ? OR creator LIKE ? OR subject LIKE ?)"
            query_params.extend([f"%{query}%"] * 4)
            filter_clauses.append(query_clause)

        if filter_clauses:
            base_query += ' WHERE ' + ' AND '.join(filter_clauses)

        # Validate and apply sorting
        valid_sort_columns = ['id', 'user_id', 'title', 'creator', 'subject', 'description']
        if sort_by and sort_by in valid_sort_columns:
            sort_order = 'DESC' if sort_order.lower() == 'desc' else 'ASC'
            base_query += f' ORDER BY {sort_by} {sort_order}'

        # Apply pagination
        base_query += ' LIMIT ? OFFSET ?'
        query_params.extend([limit, offset])

        # Execute the main query
        results = await db.execute_query(base_query, tuple(query_params))
        
        fields = ['id', 'user_id', 'title', 'creator', 'subject', 'description']
        assets = [remove_null_fields(zip_fields(fields, result)) for result in results]

        # Get the total count of assets
        total_count_query = 'SELECT COUNT(*) FROM asset'
        total_count_params = query_params[:-2]  # Exclude limit and offset for the count query
        if filter_clauses:
            total_count_query += ' WHERE ' + ' AND '.join(filter_clauses)
        total_count_result = await db.execute_query(total_count_query, tuple(total_count_params))
        total_count = total_count_result[0][0] if total_count_result else 0

        return assets, total_count
