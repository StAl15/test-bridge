from collections import deque
from webcam_demo_1 import parse_args
from threading import Thread
from webcam_demo import show_results
import numpy as np
from webcam_demo import init_model
import cv2
from webcam_demo import inference
from fastapi import FastAPI, WebSocket

# inference()
app = FastAPI()
args = {
    "config_path": "config.json",
    "device": "your_device",
    "camera_id": 0,
    "sample_length": 10,
    "drawing_fps": 30,
    "inference_fps": 15,
    "openvino": False
}
model = init_model(args['config_path'])
frame_queue = deque()


class Connection:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.strings: str = ''

    async def receive_video(self):
        while True:
            data = await self.websocket.receive_bytes()

            # Декодируем изображение из сжатого формата (например, JPEG)
            image_np = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
            print("inference")
            frame_queue.append(np.array(cv2.resize(image_np, (224, 224))[:, :, ::-1]))
            rez = inference(model)
            # pw = Thread(target=show_results, args=(image_np,), daemon=True)
            # pr = Thread(target=inference, args=(model,), daemon=True)
            # pr.start()
            print(rez)
            if image_np is not None:
                self.strings = f"{rez}"
            else:
                self.strings = "Failed to decode image"

            await self.send_strings()
        return

    async def send_strings(self):
        await self.websocket.send_json(self.strings)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    connection = Connection(websocket)
    await websocket.accept()
    await connection.send_strings()
    await connection.receive_video()
