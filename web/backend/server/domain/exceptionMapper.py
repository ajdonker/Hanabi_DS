from .exceptions import GameException, GameNotFoundException, WrongTurnException, NoTokenException, MisfireException
from web.backend.presentation.event import Event

class ExceptionMapper:

    @staticmethod
    def to_events(ex: GameException) -> list[Event]:
        
        if isinstance(ex, GameNotFoundException):
            return [Event("error", {"message": "Game not found"})]
        
        elif isinstance(ex, WrongTurnException):
            return [Event("error", {"message": "Not your turn"})]

        elif isinstance(ex, NoTokenException):
            return [Event("error", {"message": "No tokens left"})]

        elif isinstance(ex, MisfireException):
            return [
                Event("misfire", {"message": "You played a wrong card"}),
                Event("turn_change", {"playerId": ex.player_id})
            ]  
        else:
            return [Event("error", {"message": "Unknown error"})]