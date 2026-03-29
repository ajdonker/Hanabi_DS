from collections import defaultdict
from threading import Lock
from typing import Optional
from uuid import uuid4

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, WebSocket] = {}
        self.player_connections: dict[str, str] = {}
        self.game_connections: dict[str, set[str]] = defaultdict(set)
        self._conn_players: dict[str, str] = {}
        self._lock = Lock()

    def add_connection(self, websocket: WebSocket) -> str:
        conn_id = f"conn-{uuid4().hex[:12]}"
        with self._lock:
            self._connections[conn_id] = websocket
        return conn_id

    def remove_connection(self, conn_id: str) -> None:
        with self._lock:
            self._connections.pop(conn_id, None)

            player_id = self._conn_players.pop(conn_id, None)
            if player_id is not None:
                self.player_connections.pop(player_id, None)
                for game_id in list(self.game_connections.keys()):
                    self.game_connections[game_id].discard(conn_id)
                    if not self.game_connections[game_id]:
                        self.game_connections.pop(game_id, None)

    def bind_player(self, conn_id: str, player_id: str) -> None:
        with self._lock:
            self.player_connections[player_id] = conn_id
            self._conn_players[conn_id] = player_id

    def unbind_player(self, player_id: str) -> None:
        with self._lock:
            conn_id = self.player_connections.pop(player_id, None)
            if conn_id is None:
                return
            self._conn_players.pop(conn_id, None)
            for game_id in list(self.game_connections.keys()):
                self.game_connections[game_id].discard(conn_id)
                if not self.game_connections[game_id]:
                    self.game_connections.pop(game_id, None)

    def join_game(self, player_id: str, game_id: str) -> None:
        with self._lock:
            conn_id = self.player_connections.get(player_id)
            if conn_id is None:
                return
            self.game_connections[game_id].add(conn_id)

    def leave_game(self, player_id: str, game_id: str) -> None:
        with self._lock:
            conn_id = self.player_connections.get(player_id)
            if conn_id is None:
                return
            self.game_connections[game_id].discard(conn_id)
            if not self.game_connections[game_id]:
                self.game_connections.pop(game_id, None)

    def get_connection(self, player_id: str) -> Optional[WebSocket]:
        with self._lock:
            conn_id = self.player_connections.get(player_id)
            if conn_id is None:
                return None
            return self._connections.get(conn_id)

    def get_connection_by_id(self, conn_id: str) -> Optional[WebSocket]:
        with self._lock:
            return self._connections.get(conn_id)

    def get_player_for_connection(self, conn_id: str) -> Optional[str]:
        with self._lock:
            return self._conn_players.get(conn_id)

    def get_game_connections(self, game_id: str) -> list[WebSocket]:
        with self._lock:
            conn_ids = self.game_connections.get(game_id, set())
            return [self._connections[conn_id] for conn_id in conn_ids if conn_id in self._connections]

    def get_conn_ids_for_game(self, game_id: str) -> list[str]:
        with self._lock:
            return list(self.game_connections.get(game_id, set()))
