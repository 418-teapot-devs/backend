from fastapi import WebSocket


# Based on
# https://gist.github.com/francbartoli/2532f8bd8249a4cefa32f9c17c886a4b
class Notifier:
    def __init__(self):
        self.connections = []
        self.generator = self._get_notification_generator()

    async def _get_notification_generator(self):
        while True:
            msg = yield
            await self._notify(msg)

    async def push(self, msg):
        await self.generator.asend(msg)

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.append(ws)

    def remove(self, ws: WebSocket):
        self.connections.remove(ws)

    async def _notify(self, msg):
        living_connections = []
        while len(self.connections) > 0:
            # Looping like this is necessary in case a disconnection is handled
            # during await websocket.send_text(message)
            ws = self.connections.pop()
            await ws.send_json(msg)
            living_connections.append(ws)
        self.connections = living_connections
