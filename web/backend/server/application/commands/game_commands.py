from presentation.event import Event
from server.domain.cards import Color
from database.GameRepo import RedisRepository
from database.repos import IGameRepository
from server.application.commands.commands import Command
from server.domain.exceptions import *
from server.domain.game import Game
from web.backend.server.domain.exceptionMapper import ExceptionMapper

class PlayCardCommand(Command):
    def __init__(self,repo: IGameRepository):
        self.repo = repo
        
    def execute(self, data) -> list[Event]:
    
        try:
            game_id = data["gameId"] #can raise KeyError

            raw = self.repo.load_game(game_id)

            if raw is None: 
                raise GameNotFoundException()
        
            game = Game.from_dict(raw)
        
            player_id=data["playerId"]
            card_index=data["cardIndex"]
            
            game.playCard(player_id, card_index) #can raise a lot of exceptions

            self.repo.save_game(game_id,game.to_dict()) 

            return [
                Event("card_played", {"playerId": player_id, "cardIndex": card_index}),
                Event("turn_change", {"playerId": player_id})
            ]
        
        except GameException as ex:
            return ExceptionMapper.to_events(ex)
    
class DiscardCardCommand(Command):
    def __init__(self,repo: IGameRepository):
        self.repo = repo
        
    def execute(self, data) -> list[Event]:
        
        game_id = data["gameId"]
        raw = self.repo.load_game(game_id)

        if raw is None:
            return [Event("error", {"message": "Game not found"})]
        
        game = Game.from_dict(raw)

        try:
            player_id=data["playerId"]
            card_index=data["cardIndex"]
            game.discardCard(player_id, card_index)

            self.repo.save_game(game_id, game.to_dict())

            return [
                Event("card_discarded", {"playerId": player_id, "cardIndex": card_index}),
                Event("turn_change", {"playerId": player_id})
            ]
            
        except WrongTurnException :
            return [Event("error", {"message": "Not your turn"})]

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
                from_player,
                to_player,
                color,
                number
            )

            self.repo.save_game(game)

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