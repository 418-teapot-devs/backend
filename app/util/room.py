from fastapi import WebSocket

class Room:
    def __init__(self):
        self.clients = []
        flag = False

    async def connect(self, client: WebSocket):
        await client.accept()
        self.clients.append(client)

    def disconnect(self, client: WebSocket):
        self.clients.remove(client)

    async def broadcast(self, msg: str):
        for client in self.clients:
            await client.send_text(msg)
