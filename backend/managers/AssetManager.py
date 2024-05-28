from uuid import uuid4
import backend.db as db

class AssetManager:
    def __init__(self):
        db.init_db()

    async def create_asset(self, title, creator, subject, description):
        id = str(uuid4())
        query = 'INSERT INTO asset (id, title, creator, subject, description) VALUES (?, ?, ?, ?, ?)'
        await db.execute_query(query, (id, title, creator, subject, description))
        return id

    async def retrieve_all_assets(self, limit=None):
        if limit is not None:
            query = 'SELECT id, title, creator, subject, description FROM asset LIMIT ?'
            results = await db.execute_query(query, (limit,))
        else:
            query = 'SELECT id, title, creator, subject, description FROM asset'
            results = await db.execute_query(query)
        
        assets = []
        for result in results:
            assets.append({'id': result[0], 'title': result[1], 'creator': result[2], 'subject': result[3], 'description': result[4]})
        return assets

    async def retrieve_asset(self, id):
        query = 'SELECT title, creator, subject, description FROM asset WHERE id = ?'
        result = await db.execute_query(query, (id,))
        if result:
            return {'id': id, 'title': result[0][0], 'creator': result[0][1], 'subject': result[0][2], 'description': result[0][3]}
        return None

    async def update_asset(self, id, title, creator, subject, description):
        query = 'INSERT OR REPLACE INTO asset (id, title, creator, subject, description) VALUES (?, ?, ?, ?, ?)'
        return await db.execute_query(query, (id, title, creator, subject, description))

    async def delete_asset(self, id):
        query = 'DELETE FROM asset WHERE id = ?'
        return await db.execute_query(query, (id,))
