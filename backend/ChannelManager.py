import db
from paths import db_path

class ChannelManager:
    def __init__(self):
        db.init_db()

    def retrieve_all_channels(self):
        query = 'SELECT id, name, uri FROM channel'
        results = db.execute_query(query)
        channels = []
        for result in results:
            channels.append({'id': result[0], 'name': result[1], 'uri': result[2]})
        return channels

    def create_channel(self, id, name, uri):
        query = 'INSERT INTO channel (id, name, uri) VALUES (?, ?, ?)'
        db.execute_query(query, (id, name, uri))

    def retrieve_channel(self, id):
        query = 'SELECT name, uri FROM channel WHERE id = ?'
        result = db.execute_query(query, (id,))
        if result:
            return {'id': id, 'name': result[0][0], 'uri': result[0][1]}
        return None

    def update_channel(self, id, name, uri):
        query = 'INSERT OR REPLACE INTO channel (id, name, uri) VALUES (?, ?, ?)'
        db.execute_query(query, (id, name, uri))

    def delete_channel(self, id):
        query = 'DELETE FROM channel WHERE id = ?'
        db.execute_query(query, (id,))
