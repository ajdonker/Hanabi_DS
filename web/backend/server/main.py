from fastapi import FastAPI

from web.backend.server.presentation.router import ws_router


def create_app() -> FastAPI:
    app = FastAPI(title="Hanabi Backend")
    app.include_router(ws_router)
    return app


app = create_app()
