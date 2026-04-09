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
            
            #all can raise KeyError
            game_id = data["gameId"]
            player_id = data["playerId"]
            card_index = data["cardIndex"]
            
            raw = self.repo.load_game(game_id)
            if raw is None: 
                raise GameNotFoundException()
        
            game = Game.from_dict(raw)
                
            result = game.playCard(player_id, card_index) #can raise exceptions

            self.repo.save_game(game_id,game.to_dict()) 
            
            events = []

            if result.success :
               events.append(Event("card_correct", {"playerId": player_id, "cardIndex": card_index}))
            else :    
                events.append(Event("card_wrong", {"playerId": player_id, "cardIndex": card_index}))
                events.append(Event("misfire", {"playerId": player_id, "misfire" : result.misfire}))
            
            if result.game_over :
                events.append(Event("game_over", {"score" : result.score}))
                return events

            events.append(Event("turn_change", {"next_player" : result.nextPlayer}))
            
            return events           
        
        except GameException as ex:
            return ExceptionMapper.to_events(ex)
    
class DiscardCardCommand(Command):
    def __init__(self,repo: IGameRepository):
        self.repo = repo
        
    def execute(self, data) -> list[Event]:
        
        try:
            game_id = data["gameId"]
            player_id=data["playerId"]
            card_index=data["cardIndex"]
            
            raw = self.repo.load_game(game_id)
            if raw is None:
                return [Event("error", {"message": "Game not found"})]
        
            game = Game.from_dict(raw)

            result = game.discardCard(player_id, card_index)

            self.repo.save_game(game_id, game.to_dict())

            events = []
            
            if result.success :
               events.append(Event("card_discarded", {"playerId": player_id, "cardIndex": card_index}))
            else :    
                pass # it's impossible failing to discard a card
            
            if result.game_over :
                events.append(Event("game_over", {"score" : result.score}))
                    
            events.append(Event("turn_change", {"next_player" : result.nextPlayer}))
                        
            return events
            
        except GameException as ex:
            return ExceptionMapper.to_events(ex)

class GiveHintCommand(Command):
    def __init__(self,repo: IGameRepository):
        self.repo = repo

    def execute(self, data):
    
        try:
            game_id = data["gameId"]
            from_player = data["fromPlayerId"]
            to_player = data["toPlayerId"]
            color = data["color"]
            number = data["number"]

            raw = self.repo.load_game(game_id)
            if raw is None:
                return [Event("error", {"message": "Game not found"})]
        
            game = Game.from_dict(raw)

            result = game.giveHint(from_player,to_player,color,number)

            self.repo.save_game(game)

            events = []
            
            #todo
            if result.success : #hint successful
               events.append(Event("hint_given", {
                    "fromPlayerId": from_player, 
                    "toPlayerId": to_player,
                    "color": color,
                    "number": number,
                    "tokensLeft" : result.tokensLeft
                }))
            else :    
                events.append(Event("hint_failed", {
                    "fromPlayerId": from_player, 
                    "toPlayerId": to_player,
                    "color": color,
                    "number": number,
                    "tokensLeft" : result.tokensLeft
                }))
            
            if result.game_over :
                events.append(Event("game_over", {"score" : result.score}))
                    
            events.append(Event("turn_change", {"next_player" : result.nextPlayer}))
                        
            return events
        
        except GameException as ex:
            return ExceptionMapper.to_events(ex)