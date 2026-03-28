from abc import ABC,abstractmethod
from game_logic.cards import Color

class Command(ABC):
    @abstractmethod
    def execute(self,server,msg):
        pass

class PlayCardCommand(Command):
    def execute(self, server, msg):
        server.game.play_card(msg["player_idx"], msg["card_idx"])

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