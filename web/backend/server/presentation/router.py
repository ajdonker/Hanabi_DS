from fastapi import APIRouter, WebSocket

from web.backend.server.application.bootstrap import build_command_dispatcher
from web.backend.server.presentation.connection_manager import ConnectionManager
from web.backend.server.presentation.handler import WebSocketHandler

ws_router = APIRouter()


_command_dispatcher = build_command_dispatcher()
_connection_manager = ConnectionManager()
_websocket_handler = WebSocketHandler(
    dispatcher=_command_dispatcher,
    connection_manager=_connection_manager,
)


@ws_router.websocket("/ws")
async def ws_endpoint(websocket: WebSocket) -> None:
    print("WebSocket connection established.")
    await _websocket_handler.main(websocket)
