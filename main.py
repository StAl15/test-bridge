import time
# from webcam_demo import init_model
# from webcam_demo import show_results
# from webcam_demo import parse_args
# from model import Predictor
# from webcam_demo import inference
from fastapi import FastAPI, WebSocket
from typing import List
import cv2
import numpy as np

# args = parse_args()
# model = init_model('config.json')
app = FastAPI()


class Connection:
    def init(self, websocket: WebSocket):
        self.websocket = websocket
        self.strings: str = ''

    async def receive_video(self):
        while True:
            data = await self.websocket.receive_bytes()
            image = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), -1)  # Преобразовать bytes в изображение
            await self.print_pixel_matrix(image)

            # Допустим, вы знаете ширину и высоту изображения
            # width, height = 640, 480
            # Конвертирование массива байтов в матрицу пикселей
            image_np = np.frombuffer(data, dtype=np.uint8).reshape()

            # Ваш код для работы с матрицей пикселей (например, отображение изображения)
            cv2.imshow('image', image_np)
            cv2.waitKey(1)
            # results = inference(model, image_np)
            # self.strings = f"{results}"
            await self.send_strings()

    async def print_pixel_matrix(self, image):
        print(image)

    async def send_strings(self):
        await self.websocket.send_json(self.strings)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    connection = Connection(websocket)
    await websocket.accept()
    await connection.send_strings()
    await connection.receive_video()
