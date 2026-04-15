from dataclasses import dataclass

@dataclass
class WaitingPlayer: # contains only the data needed to keep in check waiting players in queue
    def __init__(self, player_id  : str, lobby_id : str):
        self.player_id = player_id
        self.lobby_id = lobby_id
  
