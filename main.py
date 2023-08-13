import numpy as np
import cv2
from fastapi import FastAPI, WebSocket

app = FastAPI()


class Connection:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.strings: str = ''

    async def receive_video(self):
        while True:
            data = await self.websocket.receive_bytes()

            # Декодируем изображение из сжатого формата (например, JPEG)
            image_np = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)

            if image_np is not None:
                self.strings = f"Received image of size {image_np.shape[1]}x{image_np.shape[0]}"
            else:
                self.strings = "Failed to decode image"

            await self.send_strings()

    async def send_strings(self):
        await self.websocket.send_json(self.strings)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    connection = Connection(websocket)
    await websocket.accept()
    await connection.send_strings()
    await connection.receive_video()
