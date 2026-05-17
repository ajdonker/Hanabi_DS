import asyncio
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.presentation.router import _connection_manager, ws_router
from database.RedisRepository import RedisRepository
from server.presentation.turnWatcher import TurnWatcher

repo = RedisRepository()

def create_app() -> FastAPI:
    app = FastAPI(title="Hanabi Backend")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.repo = repo
    app.include_router(ws_router)
    return app

app = create_app()

@app.on_event("startup")
async def startup():
    if os.getenv("IS_GAME_SERVER") != "1":
        print("[Server] TurnWatcher skipped in hanabi-server container")
        return

    game_id = os.getenv("GAME_ID")
    if not game_id:
        print("[Server] TurnWatcher skipped: GAME_ID missing")
        return

    watcher = TurnWatcher(repo, _connection_manager, game_id)
    asyncio.create_task(watcher.start())
    print(f"[Server] TurnWatcher started for game {game_id}")


@app.on_event("shutdown")
async def shutdown():
    is_game_server = os.getenv("IS_GAME_SERVER") == "1"
    if is_game_server:
        return

    repo.delete_player_game_mappings()
    print("[Server] Cleared player-game mappings")
