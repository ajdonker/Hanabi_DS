from .exceptions import GameException, GameNotFoundException, WrongTurnException, NoTokenException, MisfireException
from server.presentation.websocket_handler import Event

class ExceptionMapper:

    @staticmethod
    def to_events(ex: GameException) -> list[Event]:
        
        if isinstance(ex, GameNotFoundException):
            return [Event("error", {"message": "Game not found"})]
        
        elif isinstance(ex, WrongTurnException):
            return [Event("error", {"message": "Not your turn"})]

        else:
            return [Event("error", {"message": "Unknown error"})]