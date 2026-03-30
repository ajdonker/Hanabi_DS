# python -m uvicorn web.backend.server.main:app --reload --host 0.0.0.0 --port 8000
from fastapi import FastAPI

from web.backend.server.presentation.router import ws_router


def create_app() -> FastAPI:
    app = FastAPI(title="Hanabi Backend")
    app.include_router(ws_router)
    return app


app = create_app()
