# python -m uvicorn server.main:app --reload --host 0.0.0.0 --port 8000
import asyncio

from fastapi import FastAPI
from server.presentation.router import _connection_manager, ws_router
from database.RedisRepository import RedisRepository
from server.presentation.turnWatcher import TurnWatcher

repo = RedisRepository()

def create_app() -> FastAPI:
    app = FastAPI(title="Hanabi Backend")
    app.state.repo = repo
    app.include_router(ws_router)
    return app

app = create_app()

@app.on_event("startup")
async def startup():
    watcher = TurnWatcher(repo, _connection_manager)
    asyncio.create_task(watcher.start())
    print("[Server] TurnWatcher started")
