from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .handler import SessionMessageHandler
import json

app = FastAPI()
handler = SessionMessageHandler()


@app.get('/')
async def health_check():
    return {'status': 'ok'}


@app.websocket('/ws/python')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            msg = await websocket.receive_text()
            data = json.loads(msg)
            handler.handle_message(data, websocket)

    except WebSocketDisconnect:
        print('connect close')
    except Exception as e:
        print('websocket error :', e)
