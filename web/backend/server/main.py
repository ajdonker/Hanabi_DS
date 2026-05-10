import asyncio
import os

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


@app.on_event("shutdown")
async def shutdown():
    is_game_server = os.getenv("IS_GAME_SERVER") == "1"
    if is_game_server:
        return

    repo.delete_player_game_mappings()
    print("[Server] Cleared player-game mappings")
