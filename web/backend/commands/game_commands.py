from presentation import Event
from game_logic.cards import Color
from infrastructure.redis_provider import RedisGameRepository
from web.backend.commands.commands import Command
from web.backend.commands.exceptions import *

class PlayCardCommand(Command):
    def __init__(self):
        self.gameRepository = RedisGameRepository()
        
    def execute(self, data):
        
        game = self.game_repository.get(data["gameId"])

        try:
            player_id=data["playerId"],
            card_index=data["cardIndex"]
            game.play_card(player_id, card_index)

            self.game_repository.save(game)

            return [
                Event("card_played", {"playerId": player_id, "cardIndex": card_index}),
                Event("turn_change", {"playerId": player_id})
            ]
            
        except WrongTurnException as e:
            return [
                Event("error", {"message": "Not your turn"})
            ]
    
class DiscardCardCommand(Command):
    def execute(self, server, msg):
        server.game.discard(msg["player_idx"], msg["card_idx"])

class GiveHintCommand(Command):
    def execute(self, server, msg):
        if "color" in msg:
            server.game.give_hint(
                msg["from"],
                msg["to"],
                color=Color[msg["color"]]
            )
        elif "number" in msg:
            server.game.give_hint(
                msg["from"],
                msg["to"],
                number=msg["number"]
            )
        else:
            raise ValueError("Hint must contain color or number")