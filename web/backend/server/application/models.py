from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class User:
    id: str
    username: str


class CommandError(Exception):
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


@dataclass(frozen=True)
class Event:
    event: str
    data: dict[str, Any]


@dataclass
class CommandMessage:
    type: str
    action: str
    data: dict[str, Any]
    request_id: Optional[str] = None
    connection_id: Optional[str] = None
