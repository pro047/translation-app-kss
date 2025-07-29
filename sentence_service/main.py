from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from .websocket_server import start_websocket_server, wait_for_websocket_ready


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🟢 FastAPI 시작")
    task = asyncio.create_task(start_websocket_server())
    await wait_for_websocket_ready()
    yield
    print('🔴 FasetAPI 종료')

app = FastAPI(lifespan=lifespan)
