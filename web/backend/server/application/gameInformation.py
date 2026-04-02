class GameInformation: # to keep active games, manage their state ON/OFF
    def __init__(self, game_id, container_name, host, port, players,timestamp):
        self.game_id = game_id #reference to Game class in domain ??
        self.container_name = container_name
        self.host = host
        self.port = port
        self.players = players   # list of str
        self.status = "running"
        self.timestamp = timestamp
