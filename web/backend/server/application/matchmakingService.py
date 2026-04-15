import time
import uuid
from database.RedisRepository import RedisRepository
from server.application.gameInformation import GameInformation
from server.application.waitingPlayer import WaitingPlayer
from server.application.gameManagerService import GameServerManager
from server.domain.exceptions import LobbyException

class MatchmakingService:

    def __init__(self, repository):
        self.waiting_players = list[WaitingPlayer] # list of WaitingPlayer objects, example: [WaitingPlayer(player_id="1234", lobby_id="lobby1")]
        self.active_games = {} #list of GameInformation objects, example: {"game_id": "g01", GameInformation}
        self.active_player_names = {} #example: {"alice": {"status": "active","game_id": "1234"}, "bob": {"status": "active","game_id": "1234"}}
        self.lobbies = {} # example: {"lobby_id" : 001, "players": ["alice", "bob"], "max_players": 4}
        self.gameServer_manager = GameServerManager()
        self.matchmakerRepository = repository or RedisRepository()

    def create_lobby(self, lobby_id: str, max_users: int, user_creator : str):
        
        if lobby_id in self.lobbies:
            raise LobbyException
        
        self.lobbies[lobby_id] = {
            "players": [user_creator],
            "max_players": max_users
        }

    def join_lobby(self, user_joined : str, lobby_id: str) -> str: 
        
        if lobby_id not in self.lobbies:
            raise LobbyException #lobby not found
        
        player = WaitingPlayer(user_joined, lobby_id)
        self.waiting_players.append(player)
        
        lobby = self.lobbies[lobby_id]    
        
        #count all players in the pool that are in the same lobby
        lobby_players = [p for p in self.waiting_players if p.lobby_id == lobby_id]
        
        if len(lobby_players) < lobby["max_users"]:
            return "WAITING"
        
        self.create_game(lobby_players, lobby_id, game_id = str(uuid.uuid4())[:8])
        
        return "GAME_CREATED"
    
    def create_game(self,lobby_players,lobby_id, game_id):
 
        for p in lobby_players:
            self.active_player_names[p.name] = {"status": "active","game_id": game_id}
        
        try: 
            self.matchmakerRepository.save_player_game(lobby_id, game_id)
        except RuntimeError:
            raise RuntimeError #to be handled
            
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
        
        try: 
            self.matchmakerRepository.save_game_server(
            game_id= game_id,
            host = game.host,
            port = game.port,
            container= game.container_name
            )
        except RuntimeError:
            raise RuntimeError #to be handled
        
        return game
    
    #useful methods for handling disconnections and finding games    
    #to be moved in presentation
    def remove_waiting_player(self, conn):
        with self.lock:
            removed_names = [p.name for p in self.waiting_players if p.conn == conn]
            self.waiting_players = [p for p in self.waiting_players if p.conn != conn]
            for name in removed_names:
                self.active_player_names.pop(name, None)

    #good for reconnecting protocol
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
    
