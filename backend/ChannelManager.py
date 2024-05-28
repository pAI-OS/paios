from uuid import uuid4
import backend.db as db

class ChannelManager:
    def __init__(self):
        db.init_db()

    async def retrieve_all_channels(self, limit=None):
        if limit is not None:
            query = 'SELECT id, name, uri FROM channel LIMIT ?'
            results = await db.execute_query(query, (limit,))
        else:
            query = 'SELECT id, name, uri FROM channel'
            results = await db.execute_query(query)
        
        channels = []
        for result in results:
            channels.append({'id': result[0], 'name': result[1], 'uri': result[2]})
        return channels

    async def create_channel(self, name, uri):
        id = str(uuid4())
        query = 'INSERT INTO channel (id, name, uri) VALUES (?, ?, ?)'
        await db.execute_query(query, (id, name, uri))
        return id

    async def retrieve_channel(self, id):
        query = 'SELECT name, uri FROM channel WHERE id = ?'
        result = await db.execute_query(query, (id,))
        if result:
            return {'id': id, 'name': result[0][0], 'uri': result[0][1]}
        return None

    async def update_channel(self, id, name, uri):
        query = 'INSERT OR REPLACE INTO channel (id, name, uri) VALUES (?, ?, ?)'
        await db.execute_query(query, (id, name, uri))

    async def delete_channel(self, id):
        query = 'DELETE FROM channel WHERE id = ?'
        await db.execute_query(query, (id,))
