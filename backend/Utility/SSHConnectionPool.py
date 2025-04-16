import asyncio
import asyncssh
from flask import current_app
import uuid

class SSHConnectionPool:
    def __init__(self):
        self.connections = {}  

    async def _create_connection(self, host, username):
        connection_id = str(uuid.uuid4())
        try:
            connection = await asyncssh.connect(
                host,
                username=username,
                client_keys=[current_app.config.get('Z_KEY_PATH')],
                port=22
            )
            self.connections[connection_id] = connection
            return connection_id, connection
        except Exception as e:
            print(f"Error creating SSH connection: {e}")
            return None, None

    async def get_connection(self, connection_id=None): 
        if connection_id:
            if connection_id in self.connections:
                return self.connections[connection_id]
            else:
                return None

    async def release_connection(self, connection_id):
        if connection_id in self.connections:
            return self.connections[connection_id]
        else:
            return None

    async def close_connection(self, connection_id):
        if connection_id in self.connections:
            connection = self.connections.pop(connection_id)
            connection.close()
            return True
        else:
            return False

    async def close_all(self):
        for connection in self.connections.values():
            connection.close()
        self.connections.clear()

