from presentation import Event
from web.backend.server.domain import Color
from infrastructure.redis_provider import RedisRepository
from web.backend.commands.commands import Command
from web.backend.server.domain.exceptions import *

class PlayCardCommand(Command):
    def __init__(self):
        self.gameRepository = RedisRepository()
        
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
            
        except WrongTurnException :
            return [
                Event("error", {"message": "Not your turn"})
            ]
        
        except MisfireException :
            return [
                Event("misfire", {"message": "You played a wrong card"}),
                Event("turn_change", {"playerId": player_id})
            ]      
    
class DiscardCardCommand(Command):
    def __init__(self):
        self.gameRepository = RedisRepository()
        
    def execute(self, data):
        
        game = self.game_repository.get(data["gameId"])

        try:
            player_id=data["playerId"],
            card_index=data["cardIndex"]
            game.play_card(player_id, card_index)

            self.game_repository.save(game)

            return [
                Event("card_discarded", {"playerId": player_id, "cardIndex": card_index}),
                Event("turn_change", {"playerId": player_id})
            ]
            
        except WrongTurnException as e:
            return [
                Event("error", {"message": "Not your turn"})
            ]

class GiveHintCommand(Command):
    pass #todo