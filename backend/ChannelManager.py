import db
from paths import db_path

class ChannelManager:
    def __init__(self):
        db.init_db()

    def create_channel(self, id, name, uri):
        query = 'INSERT INTO channel (id, name, uri) VALUES (?, ?, ?)'
        db.execute_query(query, (id, name, uri))

    def retrieve_channel(self, id):
        query = 'SELECT name, uri FROM channel WHERE id = ?'
        result = db.execute_query(query, (id,))
        if result:
            return {'name': result[0][0], 'uri': result[0][1]}
        return None

    def update_channel(self, id, name, uri):
        query = 'UPDATE channel SET name = ?, uri = ? WHERE id = ?'
        db.execute_query(query, (name, uri, id))

    def delete_channel(self, id):
        query = 'DELETE FROM channel WHERE id = ?'
        db.execute_query(query, (id,))
