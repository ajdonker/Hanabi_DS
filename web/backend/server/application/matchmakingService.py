import time
import uuid
import threading
from server.application.gameInformation import GameInformation
from server.application.waitingPlayer import WaitingPlayer
from server.application.gameServerManager import GameServerManager
from server.events import Event
from database.RedisRepository import RedisRepository
from server.domain.exceptions import LobbyException

SERVER_TIMEOUT_TIME = 50000

class MatchmakingService:

    def __init__(self, repo=None):
        self.waiting_players = [] # list of WaitingPlayer objects, example: [WaitingPlayer(player_id="1234", name="alice", lobby_id="lobby1")]
        self.active_games = {} #list of GameInformation objects, example: {"game_id": GameInformation}
        self.active_player_names = {str, dict[str,int]} #example: {"alice": {"status": "active","game_id": "1234"}, "bob": {"status": "active","game_id": "1234"}}
        self.lobbies = {int, dict[list[str], int]} # example: {"lobby_id" : 123, {"players": ["alice", "bob"], max_players: 4}}
        self.repo = repo if repo is not None else RedisRepository()
        self.gameServerManager = GameServerManager()
        self.lock = threading.RLock()
        
    #added
    def create_lobby(self, lobby_id: str, max_users: int, user_creator : str) -> str:
        with self.lock:
            if lobby_id in self.lobbies:
                raise LobbyException("Lobby already exists") #to be handled in lobby comands

            self.lobbies[lobby_id] = {
                "players": [user_creator],
                "max_users": max_users
            }

        return "LOBBY_CREATED"

    #added
    def join_lobby(self, lobby_id: str, player : WaitingPlayer) -> str:
        with self.lock:
            if lobby_id not in self.lobbies:
                raise LobbyException

            result = self.add_player_to_pool(player, lobby_id)
        
        return result
    
    def add_player_to_pool(self, player: WaitingPlayer, lobby_id: str) -> str: 
        
        if any(p.name == player.name and p.lobby_id == lobby_id for p in self.waiting_players):
            return "ALREADY_IN_QUEUE"
        
        self.waiting_players.append(player)
        lobby = self.lobbies[lobby_id]    
        lobby.players.append(player.name)
        #count all players in the pool that are in the same lobby
        lobby_players = [p for p in self.waiting_players if p.lobby_id == lobby_id]
        
        if len(lobby_players) < lobby["max_users"]:
            return "WAITING"

        self.waiting_players = [p for p in self.waiting_players if p.lobby_id != lobby_id]
        game_id = str(uuid.uuid4())[:8]

        self.create_game(lobby_players, game_id)
            
        return "MATCH_FOUND"
    
    def create_game(self,lobby_players, game_id):
        
        with self.lock:
            for p in lobby_players:
                self.active_player_names[p.name] = {"status": "active","game_id": game_id}
            
            player_names = [p.name for p in lobby_players]
            host, port, container_name = self.gameServerManager.spawn_server_container(game_id,player_names)
            
            game = GameInformation(
                game_id= game_id,
                container_name = container_name,
                host = host,
                port = port,
                players = lobby_players,
                timestamp = time.time()
            )
            self.repo.save_game_information(game)
            
            for player in lobby_players:
                self.repo.save_player_game_mapping(player.name, game_id)
            
            self.active_games[game_id] = game
            return game
    
    def remove_game(self, game_id):
        with self.lock:
            game = self.active_games.pop(game_id, None)
            if not game:
                return
            
            for p in game.players:
                self.active_games.pop(p.name, None)

        removed = self.gameServerManager.remove_container(game.container_name)
        if not removed:
            print(f"Cleanup failed for {game_id}: could not remove container {game.container_name}")
    
    #useful methods for handling disconnections and finding games    

    def cleanup_games(self):
        with self.lock:
            to_remove = []
            now = time.time()

            for game_id, game in self.active_games.items():
                status = self.gameServerManager.get_container_status(game.container_name)
                too_old = (now - game.timestamp) > SERVER_TIMEOUT_TIME
                dead = status in (None, "exited", "dead")

                if too_old or dead:
                    to_remove.append(game_id)

        for game_id in to_remove:
            print(f"[MATCHMAKER] Cleaning up expired/dead game {game_id}")
            self.remove_game(game_id)
            
    def remove_waiting_player(self, player_name: str):
        with self.lock:
            self.waiting_players = [
                p for p in self.waiting_players if p.name != player_name
            ]
            self.active_player_names.pop(player_name, None)

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