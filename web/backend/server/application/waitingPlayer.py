class WaitingPlayer: # contains only the data needed to keep in check waiting players in q 
    def __init__(self, player_id, name, conn):
        self.player_id = player_id
        self.name = name
        self.conn = conn
