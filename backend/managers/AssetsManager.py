from uuid import uuid4
import backend.db as db

class AssetsManager:
    def __init__(self):
        db.init_db()

    async def create_asset(self, user_id, title, creator, subject, description):
        id = str(uuid4())
        query = 'INSERT INTO asset (id, user_id, title, creator, subject, description) VALUES (?, ?, ?, ?, ?, ?)'
        await db.execute_query(query, (id, user_id, title, creator, subject, description))
        return id

    async def retrieve_all_assets(self, limit=None):
        if limit is not None:
            query = 'SELECT id, user_id,title, creator, subject, description FROM asset LIMIT ?'
            results = await db.execute_query(query, (limit,))
        else:
            query = 'SELECT id, user_id, title, creator, subject, description FROM asset'
            results = await db.execute_query(query)
        
        assets = []
        for result in results:
            assets.append({'id': result[0], 'user_id': result[1], 'title': result[2], 'creator': result[3], 'subject': result[4], 'description': result[5]})
        return assets

    async def retrieve_asset(self, id):
        query = 'SELECT user_id, title, creator, subject, description FROM asset WHERE id = ?'
        result = await db.execute_query(query, (id,))
        if result:
            return {'id': id, 'user_id': result[0][0], 'title': result[0][1], 'creator': result[0][2], 'subject': result[0][3], 'description': result[0][4]}
        return None

    async def update_asset(self, id, user_id, title, creator, subject, description):
        query = 'INSERT OR REPLACE INTO asset (id, user_id, title, creator, subject, description) VALUES (?, ?, ?, ?, ?, ?)'
        return await db.execute_query(query, (id, user_id, title, creator, subject, description))

    async def delete_asset(self, id):
        query = 'DELETE FROM asset WHERE id = ?'
        return await db.execute_query(query, (id,))
