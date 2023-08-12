import time

from fastapi import FastAPI, WebSocket
from typing import List

app = FastAPI()


class Connection:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.strings: str = ''

    async def receive_video(self):
        while True:
            data = await self.websocket.receive_bytes()
            self.strings = f"Received data of size {len(data)} bytes"
            await self.send_strings()

    async def send_strings(self):
        await self.websocket.send_json(self.strings)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    connection = Connection(websocket)
    await websocket.accept()
    await connection.send_strings()
    await connection.receive_video()
