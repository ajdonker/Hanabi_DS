
from server.domain.exceptions import *
from server.domain.cards import Color,Number

class PlayCardCommand():
    def __init__(self, game_id: str, player_id: str, card_index: int):
        self.game_id = game_id
        self.player_id = player_id
        self.card_index = card_index
        
    
class DiscardCardCommand():
    def __init__(self, game_id: str, player_id: str, card_index: int):
        self.game_id = game_id
        self.player_id = player_id
        self.card_index = card_index
        
class GiveHintCommand():
    def __init__(self,game_id: str, from_player: str,to_player: str,color: Color, number: Number):
        self.game_id = game_id
        self.from_player = from_player
        self.to_player = to_player
        self.color = color
        self.number = number


class GetGameStateCommand():
    def __init__(self, game_id: str):
        self.game_id = game_id
