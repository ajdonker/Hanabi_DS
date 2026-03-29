import copy
from threading import Lock
from typing import Optional
from uuid import uuid4

from web.backend.server.application.models import CommandError, CommandMessage, Event, User


class Login:
    def __init__(self) -> None:
        self._users_by_id: dict[str, User] = {}
        self._users_by_username: dict[str, str] = {}
        self._lock = Lock()

    @staticmethod
    def _required_username(data: dict[str, object]) -> str:
        value = data.get("username")
        if not isinstance(value, str):
            raise CommandError("Missing or invalid 'username'.", details={"field": "username"})
        cleaned = value.strip()
        if not cleaned:
            raise CommandError("Missing or invalid 'username'.", details={"field": "username"})
        return cleaned

    def _find_by_username(self, username: str) -> Optional[User]:
        normalized = username.lower()
        with self._lock:
            user_id = self._users_by_username.get(normalized)
            user = self._users_by_id.get(user_id) if user_id else None
            return copy.deepcopy(user) if user else None

    def _save(self, user: User) -> None:
        with self._lock:
            self._users_by_id[user.id] = copy.deepcopy(user)
            self._users_by_username[user.username.lower()] = user.id

    def execute(self, message: CommandMessage) -> list[Event]:
        username = self._required_username(message.data)
        user = self._find_by_username(username)
        if user is None:
            user = User(id=f"player-{uuid4().hex[:8]}", username=username)
            self._save(user)

        return [
            Event(
                event="player_logged",
                data={
                    "playerId": user.id,
                    "username": user.username,
                },
            )
        ]
