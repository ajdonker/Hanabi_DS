import time
import uuid
from server.application.gameInformation import GameInformation
from server.application.waitingPlayer import WaitingPlayer
from server.application.gameManagerService import GameServerManager

class MatchmakingService:

    def __init__(self):
        self.waiting_players = [] # list of WaitingPlayer objects, example: [WaitingPlayer(player_id="1234", name="alice", lobby_id="lobby1")]
        self.active_games = {} #list of GameInformation objects, example: {"game_id": GameInformation}
        self.active_player_names = {} #example: {"alice": {"status": "active","game_id": "1234"}, "bob": {"status": "active","game_id": "1234"}}
        self.lobbies = {} # example: {"lobby_id" : 001, "players": ["alice", "bob"], "max_players": 4}
        self.gameServer_manager = GameServerManager()
        
    #added
    def create_lobby(self, lobby_id: str, max_users: int, user_creator : str) -> str:
        
        if lobby_id in self.lobbies:
            raise Exception("Lobby already exists") #to be handled in lobby comands

        self.lobbies[lobby_id] = {
            "players": [user_creator],
            "max_users": max_users
        }

        return "LOBBY_CREATED"

    def join_lobby(self, player: WaitingPlayer, lobby_id: str) -> str: 
        
        if lobby_id not in self.lobbies:
            raise Exception("Lobby not found")
        
        self.waiting_players.append(player)
        lobby = self.lobbies[lobby_id]    
        #count all players in the pool that are in the same lobby
        lobby_players = [p for p in self.waiting_players if p.lobby_id == lobby_id]
        
        if len(lobby_players) < lobby["max_users"]:
            return "WAITING"

        game_id = str(uuid.uuid4())[:8]

        game = self.create_game(lobby_players, game_id)
        
        return game
    
    def create_game(self,lobby_players, game_id):
 
        for p in lobby_players:
            self.active_player_names[p.name] = {"status": "active","game_id": game_id}
        
        player_names = [p.name for p in lobby_players]
        host, port, container_name = self.gameServer_manager.spawn_server_container(game_id,player_names)
        
        game = GameInformation(
            game_id= game_id,
            container_name = container_name,
            host = host,
            port = port,
            players = lobby_players,
            timestamp = time.time()
        )
        self.active_games[game_id] = game
        return game
    
    #useful methods for handling disconnections and finding games    
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
    
    #util setter
    def setLobbySize(self, lobby_size):
        self.lobby_size = lobby_size