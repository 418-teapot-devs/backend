from fastapi import WebSocket
from typing import Dict
from app.schemas.match import Host, MatchCreateRequest, MatchResponse, RobotInMatch, MatchResponseS
import asyncio

class Room:
    def __init__(self):
        self.clients = []
        self.event = asyncio.Event()

    async def connect(self, client: WebSocket):
        await client.accept()
        self.clients.append(client)

    def disconnect(self, client: WebSocket):
        self.clients.remove(client)

    async def broadcast(self, m):
        for client in self.clients:
            # await client.send_text(msg)
            await client.send_json(m)
