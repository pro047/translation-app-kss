import json
import websockets
from .handler import SessionMessageHandler


NODE_WS_URL = "ws://127.0.0.1:5001/ws/python"

handler = SessionMessageHandler()
connected_clients = set()


async def handle_connection(websocket):
    print('node js connected')
    connected_clients.add(websocket)

    try:
        await receive_text(websocket)

    except Exception as e:
        print('connection error:', e)

    finally:
        connected_clients.remove(websocket)
        print('connection close')


async def receive_text(websocket):
    async for message in websocket:
        try:
            data = json.loads(message)
            handler.handle_message(data, websocket)

        except Exception as e:
            print('receive data error :', e)


async def start_websocket_server():
    await websockets.serve(handle_connection, '127.0.0.1', 8765)
    print('python websocket 서버 실행 중 (ws://localhost:8765)')
