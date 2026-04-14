from fastapi import APIRouter, WebSocket

from server.presentation.connection_manager import ConnectionManager
from server.presentation.websocket_handler import WebSocketHandler

ws_router = APIRouter()


_connection_manager = ConnectionManager()
_websocket_handler = WebSocketHandler(
    connection_manager=_connection_manager,
)


@ws_router.websocket("/ws")
async def ws_endpoint(websocket: WebSocket) -> None:
    await _websocket_handler.main(websocket)
