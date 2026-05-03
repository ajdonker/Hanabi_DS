from database.repos import IGameRepository
from database.gameSerializer import GameSerializer
from server.events import Event
from.handler import IHandler
from server.domain.exceptions import *
from server.domain.exceptionMapper import ExceptionMapper
from server.application.commands.game_commands import PlayCardCommand,GiveHintCommand,DiscardCardCommand,GetGameStateCommand


def create_card_drawn_event(player_id: str, result) -> Event | None:
    if result.drawn_card is None or result.drawn_card_index is None:
        return None

    return Event("card_drawn", {
        "playerId": player_id,
        "cardIndex": result.drawn_card_index,
        "card": {
            "number": result.drawn_card.number.name,
            "color": result.drawn_card.color.name,
        },
    })


class GetGameStateHandler(IHandler):
    def __init__(self, repo: IGameRepository):
        self.repo = repo

    def execute(self, command: GetGameStateCommand) -> list[Event]:
        try:
            game = self.repo.load_game(command.game_id)
            if game is None:
                raise GameNotFoundException()

            events = []
            if command.player_name:
                events.append(Event("player_joined_game", {
                    "player_name": command.player_name,
                    "game_id": command.game_id,
                }))

            events.append(Event("game_state", GameSerializer.to_dict(game)))
            return events

        except GameException as ex:
            return ExceptionMapper.to_events(ex)

        except RuntimeError:
            return [Event("error", {"message": "Temporary server issue"})]

class PlayCardHandler(IHandler):
    def __init__(self,repo: IGameRepository):
            self.repo = repo
        
    def execute(self, command: PlayCardCommand) -> list[Event]:
        try:
            game = self.repo.load_game(command.game_id)
            if game is None: 
                raise GameNotFoundException()
                        
            result = game.playCard(command.player_id, command.card_index) #can raise exceptions

            self.repo.save_game(game) 
            
            events = []

            if result.success:
               events.append(Event("card_correct", {"playerId": command.player_id, "cardIndex": command.card_index}))
            else :    
                events.append(Event("card_wrong", {"playerId": command.player_id, "cardIndex": command.card_index}))
                events.append(Event("misfire", {"playerId": command.player_id, "misfire" : result.misfire}))

            drawn_card_event = create_card_drawn_event(command.player_id, result)
            if drawn_card_event:
                events.append(drawn_card_event)
            
            if result.game_over is not None:
                events.append(Event("game_over", {"score" : result.game_over}))
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

            self.repo.save_game(game)

            events = []
            
            if result.success :
               events.append(Event("card_discarded", {"playerId": command.player_id, "cardIndex": command.card_index}))
            else :    
                pass # it's impossible failing to discard a card

            drawn_card_event = create_card_drawn_event(command.player_id, result)
            if drawn_card_event:
                events.append(drawn_card_event)
            
            if result.game_over is not None :
                events.append(Event("game_over", {"score" : result.game_over}))
                    
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

            self.repo.save_game(game)

            events = []

            if result.success:
                events.append(Event("hint_given", {
                    "fromPlayerId": command.from_player,
                    "toPlayerId": command.to_player,
                    "color": command.color.name if command.color else None,
                    "number": command.number.name if command.number else None,
                    "tokensLeft": result.tokensLeft
                }))
            else:
                events.append(Event("hint_failed", {
                    "fromPlayerId": command.from_player,
                    "toPlayerId": command.to_player,
                    "color": command.color.name if command.color else None,
                    "number": command.number.name if command.number else None,
                    "tokensLeft": result.tokensLeft
                }))

            if result.game_over is not None:
                events.append(Event("game_over", {"score": result.game_over}))

            events.append(Event("turn_change", {"next_player": result.next_player}))
            return events

        except GameException as ex:
            return ExceptionMapper.to_events(ex)

        except RuntimeError:
            return [Event("error", {"message": "Temporary server issue"})]
