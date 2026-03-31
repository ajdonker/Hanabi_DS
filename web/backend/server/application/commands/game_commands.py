from presentation.event import Event
from server.domain.cards import Color
from database.GameRepo import RedisRepository
from database.repos import IGameRepository
from commands.commands import Command
from server.domain.exceptions import *
from server.domain.game import Game

class PlayCardCommand(Command):
    def __init__(self,repo: IGameRepository):
        self.repo = repo
        
    def execute(self, data):

        game_id = data["gameId"]
        raw = self.repo.load_game(game_id)

        if raw is None:
            return [Event("error", {"message": "Game not found"})]
        
        game = Game.from_dict(raw)

        try:
            player_id=data["playerId"]
            card_index=data["cardIndex"]
            game.playCard(player_id, card_index)

            self.repo.save_game(game_id,game.to_dict())

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
    def __init__(self,repo: IGameRepository):
        self.repo = repo
        
    def execute(self, data):
        
        game_id = data["gameId"]
        raw = self.repo.load_game(game_id)

        if raw is None:
            return [Event("error", {"message": "Game not found"})]
        
        game = Game.from_dict(raw)

        try:
            player_id=data["playerId"]
            card_index=data["cardIndex"]
            game.discardCard(player_id, card_index)

            self.repo.save(game)

            return [
                Event("card_discarded", {"playerId": player_id, "cardIndex": card_index}),
                Event("turn_change", {"playerId": player_id})
            ]
            
        except WrongTurnException as e:
            return [
                Event("error", {"message": "Not your turn"})
            ]

class GiveHintCommand(Command):
    # we refactored repos so this way unsure if alrights
    def __init__(self,repo: IGameRepository):
        self.repo = repo

    def execute(self, data):
        
        game_id = data["gameId"]
        raw = self.repo.load_game(game_id)

        if raw is None:
            return [Event("error", {"message": "Game not found"})]
        
        game = Game.from_dict(raw)

        try:
            from_player = data["fromPlayerId"]
            to_player = data["toPlayerId"]
            color = data["color"]
            number = data["number"]

            game.giveHint(
                from_player_idx=from_player,
                to_player_idx=to_player,
                color=color,
                number=number
            )

            self.repo.save(game)

            return [
                Event("hint_given", {
                    "fromPlayerId": from_player, 
                    "toPlayerId": to_player,
                    "color": color,
                    "number": number
                }),
                Event("turn_change", {"playerId": from_player})
            ]

        except WrongTurnException:
            return [Event("error", {"message": "Not your turn"})]