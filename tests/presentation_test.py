import asyncio
import json
from web.backend.server.presentation.connection_manager import ConnectionManager
from web.backend.server.presentation.websocket_handler import CommandError, Event, WebSocketDisconnect, WebSocketHandler
import pytest




class DummyWebSocket:
    def __init__(self, incoming=None):
        self.accepted = False
        self.sent_texts = []
        self._incoming = list(incoming or [])

    async def accept(self):
        self.accepted = True

    async def send_text(self, payload: str):
        self.sent_texts.append(payload)

    async def receive_text(self):
        if not self._incoming:
            raise RuntimeError("No incoming messages configured")
        item = self._incoming.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def test_connection_manager_bind_join_leave_flow():
    manager = ConnectionManager()

    ws1 = DummyWebSocket()
    ws2 = DummyWebSocket()

    conn1 = manager.add_connection(ws1)
    conn2 = manager.add_connection(ws2)

    manager.bind_player(conn1, "P1")
    manager.bind_player(conn2, "P2")

    manager.join_game("P1", "g1")
    manager.join_game("P2", "g1")

    assert set(manager.get_conn_ids_for_game("g1")) == {conn1, conn2}
    assert set(manager.get_game_connections("g1")) == {ws1, ws2}
    assert manager.get_connection("P1") is ws1
    assert manager.get_player_for_connection(conn2) == "P2"

    manager.leave_game("P1", "g1")

    assert manager.get_conn_ids_for_game("g1") == [conn2]
    assert manager.get_game_connections("g1") == [ws2]


def test_connection_manager_unbind_and_remove_cleanup():
    manager = ConnectionManager()

    ws = DummyWebSocket()
    conn = manager.add_connection(ws)
    manager.bind_player(conn, "P1")
    manager.join_game("P1", "g2")

    manager.unbind_player("P1")
    assert manager.get_connection("P1") is None
    assert manager.get_player_for_connection(conn) is None
    assert manager.get_conn_ids_for_game("g2") == []

    manager.bind_player(conn, "P1")
    manager.join_game("P1", "g2")
    manager.remove_connection(conn)

    assert manager.get_connection_by_id(conn) is None
    assert manager.get_connection("P1") is None
    assert manager.get_player_for_connection(conn) is None
    assert manager.get_conn_ids_for_game("g2") == []


def test_connection_manager_join_game_with_unbound_player_is_noop():
    manager = ConnectionManager()

    manager.join_game("P2", "g1")

    assert manager.get_conn_ids_for_game("g1") == []
    assert manager.get_game_connections("g1") == []


def test_deserialize_valid_payload_and_request_id_trim():
    manager = ConnectionManager()
    handler = WebSocketHandler(manager)

    raw = json.dumps(
        {
            "type": " command ",
            "action": " player.login ",
            "requestId": " req-1 ",
        }
    )
    message = handler.deserialize(raw)

    assert message.type == "command"
    assert message.action == "player.login"
    assert message.data == {}
    assert message.request_id == "req-1"


def test_deserialize_invalid_payload_raises_command_error():
    manager = ConnectionManager()
    handler = WebSocketHandler(manager)

    with pytest.raises(CommandError) as exc_info:
        handler.deserialize('{"type": "command", "data": {}}')

    assert "Missing or invalid 'action'" in exc_info.value.message
    assert exc_info.value.details == {"field": "action"}


def test_on_message_invalid_json_sends_error_payload():
    manager = ConnectionManager()
    handler = WebSocketHandler(manager)

    ws = DummyWebSocket()
    conn = manager.add_connection(ws)

    asyncio.run(handler.on_message(conn, "{not-json"))

    assert len(ws.sent_texts) == 1
    payload = json.loads(ws.sent_texts[0])
    assert payload["type"] == "error"
    assert payload["message"] == "Invalid JSON payload."
    assert "error" in payload["details"]

# maybe fail with websocket_handler.py after adding dispatcher
def test_on_message_login_binds_player_and_returns_event_batch():
    manager = ConnectionManager()
    handler = WebSocketHandler(manager)

    ws = DummyWebSocket()
    conn = manager.add_connection(ws)

    raw = json.dumps(
        {
            "type": "command",
            "action": "player.login",
            "requestId": "r-100",
            "data": {"username": "P1"},
        }
    )
    asyncio.run(handler.on_message(conn, raw))

    assert len(ws.sent_texts) == 1
    payload = json.loads(ws.sent_texts[0])

    assert payload["type"] == "event_batch"
    assert payload["requestId"] == "r-100"
    assert len(payload["events"]) == 1
    assert payload["events"][0]["event"] == "player_logged"
    assert payload["events"][0]["data"]["username"] == "P1"

    player_id = payload["events"][0]["data"]["playerId"]
    assert manager.get_player_for_connection(conn) == player_id
    assert manager.get_connection(player_id) is ws


def test_on_message_internal_error_returns_error_with_request_id():
    manager = ConnectionManager()
    handler = WebSocketHandler(manager)

    ws = DummyWebSocket()
    conn = manager.add_connection(ws)

    def boom(_message):
        raise RuntimeError("boom")

    handler._handle_command = boom

    raw = json.dumps(
        {
            "type": "command",
            "action": "player.login",
            "requestId": "r-500",
            "data": {"username": "P2"},
        }
    )
    asyncio.run(handler.on_message(conn, raw))

    assert len(ws.sent_texts) == 1
    payload = json.loads(ws.sent_texts[0])
    assert payload["type"] == "error"
    assert payload["message"] == "Internal server error."
    assert payload["requestId"] == "r-500"
    assert payload["details"]["error"] == "boom"


def test_on_connect_accepts_websocket_and_registers_connection():
    manager = ConnectionManager()
    handler = WebSocketHandler(manager)

    ws = DummyWebSocket()
    conn = asyncio.run(handler.on_connect(ws))

    assert ws.accepted == True
    assert conn.startswith("conn-")
    assert manager.get_connection_by_id(conn) is ws


def test_main_handles_disconnect_and_cleans_connection():
    manager = ConnectionManager()
    handler = WebSocketHandler(manager)

    disconnect = WebSocketDisconnect()
    ws = DummyWebSocket(incoming=[disconnect])

    asyncio.run(handler.main(ws))

    assert ws.accepted is True
    assert manager._connections == {}

def test_broadcast_sends_event_batch_to_websocket():
    manager = ConnectionManager()
    handler = WebSocketHandler(manager)

    ws = DummyWebSocket()
    conn = manager.add_connection(ws)

    events = [
        Event("test_event", {"key": "value"})
    ]
    asyncio.run(handler.broadcast(conn, events, request_id="req-123"))

    assert len(ws.sent_texts) == 1
    payload = json.loads(ws.sent_texts[0])
    assert payload["type"] == "event_batch"
    assert payload["requestId"] == "req-123"
    assert len(payload["events"]) == 1
    assert payload["events"][0]["event"] == "test_event"
    assert payload["events"][0]["data"]["key"] == "value"
