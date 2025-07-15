from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from .websocket_server import start_websocket_server


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🟢 FastAPI 시작")
    asyncio.create_task(start_websocket_server())
    yield
    print('🔴 FasetAPI 종료')

app = FastAPI(lifespan=lifespan)
