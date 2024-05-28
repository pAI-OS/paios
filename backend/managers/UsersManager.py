from uuid import uuid4
import backend.db as db

class UsersManager:
    def __init__(self):
        db.init_db()

    async def create_user(self, name, email):
        id = str(uuid4())
        query = 'INSERT INTO user (id, name, email) VALUES (?, ?, ?)'
        await db.execute_query(query, (id, name, email))
        return id

    async def retrieve_all_users(self, limit=None):
        if limit is not None:
            query = 'SELECT id, name, email FROM user LIMIT ?'
            results = await db.execute_query(query, (limit,))
        else:
            query = 'SELECT id, name, email FROM user'
            results = await db.execute_query(query)
        
        users = []
        for result in results:
            users.append({'id': result[0], 'name': result[1], 'email': result[2]})
        return users

    async def retrieve_user(self, id):
        query = 'SELECT name, email FROM user WHERE id = ?'
        result = await db.execute_query(query, (id,))
        if result:
            return {'id': id, 'name': result[0][0], 'email': result[0][1]}
        return None

    async def update_user(self, id, name, email):
        query = 'INSERT OR REPLACE INTO user (id, name, email) VALUES (?, ?, ?)'
        return await db.execute_query(query, (id, name, email))

    async def delete_user(self, id):
        query = 'DELETE FROM user WHERE id = ?'
        return await db.execute_query(query, (id,))
