import time
import uuid
from web.backend.server.application.matchmakingService import GameInformation
from web.backend.server.application.matchmakingService import WaitingPlayer
from web.backend.server.application.gameManagerService import GameServerManager

class MatchmakingService:

    def __init__(self, lobby_size = 2):
        self.lobby_size = lobby_size 
        self.waiting_players = [] # list of WaitingPlayer objects
        self.active_games = {} #
        self.active_player_names = {} #example: {"alice": {"status": "active","game_id": "1234"}, "bob": {"status": "active","game_id": "1234"}}
        self.gameServer_manager = GameServerManager()

    def add_player_to_pool(self, player: WaitingPlayer) -> str: 
        self.waiting_players.append(player)

        if len(self.waiting_players) < self.lobby_size:
            return "WAITING"

        players = self.waiting_players[:self.lobby_size]
        self.waiting_players = self.waiting_players[self.lobby_size:]

        game_id = str(uuid.uuid4())[:8]
        player_names = [p.name for p in players]

        self.create_game(players, game_id)

        return "MATCH_FOUND"
    
    def create_game(self,players,game_id=None):
        if game_id is None:
            game_id = str(uuid.uuid4())[:8] 

        for p in players:
            self.active_player_names[p.name] = {"status": "active","game_id": game_id}
        
        player_names = [p.name for p in players]
        host, port, container_name = self.gameServer_manager.spawn_server_container(game_id,player_names)
        
        game = GameInformation(
            game_id= game_id,
            container_name = container_name,
            host = host,
            port = port,
            players = players,
            timestamp = time.time()
        )
        self.active_games[game_id] = game
        return game
    
    def remove_waiting_player(self, conn):
        with self.lock:
            removed_names = [p.name for p in self.waiting_players if p.conn == conn]
            self.waiting_players = [p for p in self.waiting_players if p.conn != conn]
            for name in removed_names:
                self.active_player_names.pop(name, None)

    def find_game(self, game_id, player_name):
        with self.lock:
            game = self.active_games.get(game_id)
            if game is None:
                return None

            player_names = [p.name for p in game.players]
            if player_name not in player_names:
                return None
            return game

    def find_game_by_player(self, player_name):
        with self.lock:
            for game in self.active_games.values():
                player_names = [p.name for p in game.players]
                print(player_names)
                if player_name in player_names:
                    print(f"Game found for player {player_name}")
                    return game
            print(f"No active game found for player {player_name}")
            return None
    
    #util
    def setLobbySize(self, lobby_size):
        self.lobby_size = lobby_size