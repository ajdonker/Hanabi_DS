# python -m uvicorn server.main:app --reload --host 0.0.0.0 --port 8000
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager

from server.presentation.router import ws_router
from server.application.turnWatcher import TurnWatcher
from database.RedisRepository import RedisRepository

def create_app() -> FastAPI:
    app = FastAPI(title="Hanabi Backend")
    app.include_router(ws_router)
    return app


app = create_app()
