from typing import Any, Optional


class GameException(Exception):
    pass

class KeyErrorException(GameException):
    pass

class IndexError(GameException):
    pass

class GameNotFoundException(GameException):
    pass

class WrongTurnException(GameException): #It's not your turn
    pass

class NoTokenException(GameException):
    pass

class MisfireException(GameException):
    pass

###################


class LobbyException(Exception):
    pass

class CommandError(Exception):
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}