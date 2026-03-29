from fastapi import APIRouter, WebSocket

from web.backend.server.presentation.connection_manager import ConnectionManager
from web.backend.server.presentation.websocket_handler import WebSocketHandler

ws_router = APIRouter()


_connection_manager = ConnectionManager()
_websocket_handler = WebSocketHandler(
    connection_manager=_connection_manager,
)


@ws_router.websocket("/ws")
async def ws_endpoint(websocket: WebSocket) -> None:
    print("WebSocket connection established.")
    await _websocket_handler.main(websocket)
