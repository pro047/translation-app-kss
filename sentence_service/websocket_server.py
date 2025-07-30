import asyncio
import json
from .handler import SessionMessageHandler


NODE_WS_URL = "wss://neemba-stt-backend.onrender.com/ws/python"

handler = SessionMessageHandler()
connected_clients = set()

_ready_event = asyncio.Event()


async def handle_connection(websocket):
    peer = websocket.remote_address
    print(f'연결됨 : ${peer}')

    connected_clients.add(websocket)

    try:
        await receive_text(websocket)

    except Exception as e:
        print(f'connection error with {peer}: {e}')

    finally:
        connected_clients.remove(websocket)
        print(f'connection close with {peer}')


async def receive_text(websocket):
    async for message in websocket:
        try:
            data = json.loads(message)
            print(data)
            handler.handle_message(data, websocket)

        except Exception as e:
            print('receive data error :', e)
