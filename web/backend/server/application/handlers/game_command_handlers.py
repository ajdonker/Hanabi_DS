from database.repos import IGameRepository
from server.events import Event
from.handler import IHandler
from server.domain.exceptions import *
from server.domain.exceptionMapper import ExceptionMapper
from server.application.commands.game_commands import PlayCardCommand,GiveHintCommand,DiscardCardCommand

class PlayCardHandler(IHandler):
    def __init__(self,repo: IGameRepository):
            self.repo = repo
        
    def execute(self, command: PlayCardCommand) -> list[Event]:
        try:
            game = self.repo.load_game(command.game_id)
            if game is None: 
                raise GameNotFoundException()
                        
            result = game.playCard(command.player_id, command.card_index) #can raise exceptions

            self.repo.save_game(command.game_id,game.to_dict()) 
            
            events = []

            if result.success:
               events.append(Event("card_correct", {"playerId": command.player_id, "cardIndex": command.card_index}))
            else :    
                events.append(Event("card_wrong", {"playerId": command.player_id, "cardIndex": command.card_index}))
                events.append(Event("misfire", {"playerId": command.player_id, "misfire" : result.misfire}))
            
            if result.game_over is not None:
                events.append(Event("game_over", {"score" : result.score}))
                return events

            events.append(Event("turn_change", {"next_player" : result.next_player}))
            
            return events           
        
        except GameException as ex:
            return ExceptionMapper.to_events(ex)

        except RuntimeError:
            return [Event("error", {"message": "Temporary server issue"})]


class DiscardCardHandler(IHandler):
    def __init__(self,repo: IGameRepository):
        self.repo = repo
        
    def execute(self, command: DiscardCardCommand) -> list[Event]:
        
        try:    
            game = self.repo.load_game(command.game_id)
            if game is None:
                raise GameNotFoundException()
        
            result = game.discardCard(command.player_id, command.card_index)

            self.repo.save_game(command.game_id, game.to_dict())

            events = []
            
            if result.success :
               events.append(Event("card_discarded", {"playerId": command.player_id, "cardIndex": command.card_index}))
            else :    
                pass # it's impossible failing to discard a card
            
            if result.game_over is not None :
                events.append(Event("game_over", {"score" : result.score}))
                    
            events.append(Event("turn_change", {"next_player" : result.next_player}))
                        
            return events
            
        except GameException as ex:
            return ExceptionMapper.to_events(ex)
        
        except RuntimeError:
            return [Event("error", {"message": "Temporary server issue"})]
        
class GiveHintHandler(IHandler):
    def __init__(self, repo: IGameRepository):
        self.repo = repo

    def execute(self, command: GiveHintCommand) -> list[Event]:
        try:
            game = self.repo.load_game(command.game_id)

            if game is None:
                raise GameNotFoundException()

            result = game.giveHint(
                command.from_player,
                command.to_player,
                command.color,
                command.number
            )

            self.repo.save_game(command.game_id, game.to_dict())

            events = []

            if result.success:
                events.append(Event("hint_given", {
                    "fromPlayerId": command.from_player,
                    "toPlayerId": command.to_player,
                    "color": command.color.value,
                    "number": command.number.value,
                    "tokensLeft": result.tokensLeft
                }))
            else:
                events.append(Event("hint_failed", {
                    "fromPlayerId": command.from_player,
                    "toPlayerId": command.to_player,
                    "color": command.color.value,
                    "number": command.number.value,
                    "tokensLeft": result.tokensLeft
                }))

            if result.game_over is not None:
                events.append(Event("game_over", {"score": result.score})) #score and tokensLeft not in result currently

            events.append(Event("turn_change", {"next_player": result.next_player}))
            return events

        except GameException as ex:
            return ExceptionMapper.to_events(ex)

        except RuntimeError:
            return [Event("error", {"message": "Temporary server issue"})]
