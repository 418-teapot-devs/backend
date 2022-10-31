import asyncio
from typing import Any, Dict

from fastapi import WebSocket

from app.schemas.match import (
    Host,
    MatchCreateRequest,
    MatchResponse,
    MatchResponseS,
    RobotInMatch,
)


class Room:
    def __init__(self):
        self.clients = []
        self.event = asyncio.Event()

    async def connect(self, client: WebSocket):
        await client.accept()
        self.clients.append(client)

    def disconnect(self, client: WebSocket):
        self.clients.remove(client)

    async def broadcast(self, m: Dict[str, Any]):
        for client in self.clients:
            await client.send_json(m)
