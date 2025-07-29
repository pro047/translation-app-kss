import asyncio
import json
import websockets
from .handler import SessionMessageHandler


NODE_WS_URL = "ws://127.0.0.1:5001/ws/python"

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


async def start_websocket_server():
    async def handler(ws, path):
        print('websocket client connected')

    async def server():
        async with websockets.serve(handle_connection, '127.0.0.1', 8765, ping_interval=30, ping_timeout=10):
            print('WebSocket 서버 준비 완료')
            _ready_event.set()
            await asyncio.Future()

        print('python websocket 서버 실행 중 (ws://localhost:8765)')
    await server()


async def wait_for_websocket_ready():
    await _ready_event.wait()
