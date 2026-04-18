import json
from dataclasses import dataclass
from typing import Any, Optional
from uuid import uuid4

from fastapi import WebSocket, WebSocketDisconnect

from server.presentation.connection_manager import ConnectionManager


class CommandError(Exception):
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


@dataclass
class CommandMessage:
    type: str
    action: str
    data: dict[str, Any]
    request_id: Optional[str] = None
    connection_id: Optional[str] = None


@dataclass(frozen=True)
class Event:
    event: str
    data: dict[str, Any]

class WebSocketHandler:
    def __init__(self, connection_manager: ConnectionManager) -> None:
        self.connection_manager = connection_manager

    def deserialize(self, raw_text: str) -> CommandMessage:
        try:
            payload = json.loads(raw_text)
        except json.JSONDecodeError as error:
            raise CommandError("Invalid JSON payload.", details={"error": str(error)}) from error

        if not isinstance(payload, dict):
            raise CommandError("Message must be a JSON object.")

        message_type = payload.get("type")
        action = payload.get("action")
        data = payload.get("data")

        if not isinstance(message_type, str) or not message_type.strip():
            raise CommandError("Missing or invalid 'type'.", details={"field": "type"})
        if not isinstance(action, str) or not action.strip():
            raise CommandError("Missing or invalid 'action'.", details={"field": "action"})
        if data is None:
            data = {}
        if not isinstance(data, dict):
            raise CommandError("Missing or invalid 'data'.", details={"field": "data"})

        request_id_raw = payload.get("requestId")
        request_id: Optional[str]
        if isinstance(request_id_raw, str) and request_id_raw.strip():
            request_id = request_id_raw.strip()
        else:
            request_id = None

        return CommandMessage(
            type=message_type.strip(),
            action=action.strip(),
            data=data,
            request_id=request_id,
        )

    def serialize(self, message: dict[str, Any]) -> str:
        return json.dumps(message)

    async def on_connect(self, websocket: WebSocket) -> str:
        await websocket.accept()
        return self.connection_manager.add_connection(websocket)

    async def on_disconnect(self, conn_id: str) -> None:
        self.connection_manager.remove_connection(conn_id)

    async def on_message(self, conn_id: str, raw_text: str) -> None:
        try:
            message = self.deserialize(raw_text)
        except CommandError as error:
            await self._send_error(conn_id, error.message, details=error.details)
            return

        message.connection_id = conn_id

        try:
            events = self._handle_command(message)
        except Exception as error:
            await self._send_error(
                conn_id,
                "Internal server error.",
                details={"error": str(error)},
                request_id=message.request_id,
            )
            return

        self._sync_connections(conn_id, events)
        await self.broadcast(conn_id, events, request_id=message.request_id)

    def _handle_command(self, message: CommandMessage) -> list[Event]:
        if message.action == "player.login": 
            return self._handle_player_login(message)
        else:
            return [
                Event(
                    event="test_event",
                    data={
                        "message": "Received unknown action",
                    },
                )
            ]

    def _handle_player_login(self, message: CommandMessage) -> list[Event]:
        username = message.data.get("username")
        user_id = str(uuid4())
        return [
            Event(
                event="player_logged",
                data={
                    "playerId": user_id,
                    "username": username,
                    "test": 131,
                },
            )
        ]
    async def broadcast(
        self,
        conn_id: str,
        events: list[Event],
        request_id: Optional[str] = None,
    ) -> None:
        payload = self._event_batch_payload(events, request_id=request_id)
        websocket = self.connection_manager.get_connection_by_id(conn_id)
        if websocket is None:
            return
        await websocket.send_text(self.serialize(payload))

    async def main(self, websocket: WebSocket) -> None:
        conn_id = await self.on_connect(websocket)
        try:
            while True:
                raw_text = await websocket.receive_text()
                await self.on_message(conn_id, raw_text)
        except WebSocketDisconnect:
            await self.on_disconnect(conn_id)

    def _sync_connections(self, conn_id: str, events: list[Event]) -> None:
        for event in events:
            if event.event == "player_logged":
                player_id = event.data.get("playerId")
                if isinstance(player_id, str) and player_id:
                    self.connection_manager.bind_player(conn_id, player_id)

    def _event_batch_payload(
        self,
        events: list[Event],
        request_id: Optional[str] = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "type": "event_batch",
            "events": [{"event": event.event, "data": event.data} for event in events],
        }
        if request_id:
            payload["requestId"] = request_id
        return payload

    async def _send_error(
        self,
        conn_id: str,
        message: str,
        details: Optional[dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> None:
        websocket = self.connection_manager.get_connection_by_id(conn_id)
        if websocket is None:
            return

        payload: dict[str, Any] = {
            "type": "error",
            "message": message,
            "details": details or {},
        }
        if request_id:
            payload["requestId"] = request_id

        await websocket.send_text(self.serialize(payload))
