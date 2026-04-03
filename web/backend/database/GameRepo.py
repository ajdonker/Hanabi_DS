from time import time

from database.repos import IGameRepository, IUserRepository
import json

from web.backend.server.application.user import User
from web.backend.server.domain.game import Game

# At any moment, there should be only one active authoritative server for a given game_id.

class RedisRepository(IGameRepository, IUserRepository):
    #Stores game states per game_id and game session related metadata 
    # - player -> game, game -> players, game ->server
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def _retry(self, func, retries=3, delay=0.2):
        for attempt in range(retries):
            try:
                return func()
            except Exception as e:
                print(f"[WARN] redis operation failed {attempt+1}/{retries}: {e}", flush=True)
                self.redis = self.redis_factory()
                time.sleep(delay)
        raise RuntimeError("Redis operation failed")

    
    #Game 
    def load_game(self, game_id : str) -> Game | None:
        key = f"hanabi:game:{game_id}"
        raw = self._retry(lambda: self.redis.get(key))
        return json.loads(raw) if raw else None

    def save_game(self, game: Game):
        key = f"hanabi:game:{game.id}"
        payload = json.dumps(game.state)
        self._retry(lambda: self.redis.set(key, payload))
    
    #User    
    def load_user(self, username : str) -> User | None:
        pass
    
    def save_user(self, user: User):
        pass
    
    def load_lobby(self, lobby_id):
        pass
    
    def save_lobby(self, lobby):
        pass
    
'''
    def save_player_game_mapping(self, player, game_id):
        key = f"hanabi:player:{player}:game"
        self._retry(lambda: self.redis.set(key, game_id))

    def get_game_id_for_player(self, player):
        key = f"hanabi:player:{player}:game"
        raw = self._retry(lambda: self.redis.get(key))
        return raw.decode() if isinstance(raw, bytes) else raw

    def save_game_players(self, game_id, players):
        key = f"hanabi:game:{game_id}:players"
        self._retry(lambda: self.redis.set(key, json.dumps(players)))

    def get_game_players(self, game_id):
        key = f"hanabi:game:{game_id}:players"
        raw = self._retry(lambda: self.redis.get(key))
        return json.loads(raw) if raw else None

    def save_server_info(self, game_id, server_info):
        key = f"hanabi:game:{game_id}:server"
        self._retry(lambda: self.redis.set(key, json.dumps(server_info)))

    def get_server_info(self, game_id):
        key = f"hanabi:game:{game_id}:server"
        raw = self._retry(lambda: self.redis.get(key))
        return json.loads(raw) if raw else None

    def clear_server_info(self, game_id):
        key = f"hanabi:game:{game_id}:server"
        self._retry(lambda: self.redis.delete(key))
'''
