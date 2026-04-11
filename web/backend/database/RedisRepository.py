from database.repos import IGameRepository, ILobbyRepository, IUserRepository
from server.domain.game import Game
import json, time, random
from web.backend.database.mockRedis import MockRedisRepository
class RedisRepository(IGameRepository, ILobbyRepository, IUserRepository):
    '''Stores game states per game_id and game session related metadata - player -> game, game -> players, game ->server'''
    def __init__(self, redis_client):
        self.redis = redis_client

    def _retry(self, fn, retries=3, base_delay=0.1):
    
        for attempt in range(retries):
            
            try:
                return fn()
            except (ConnectionError, TimeoutError) as e:
                if attempt == retries - 1:
                    raise RuntimeError("Redis operation failed") from e

                # exponential backoff + jitter
                delay = base_delay * (2 ** attempt)
                delay += random.uniform(0, 0.05)

                time.sleep(delay)
    
    def load_game(self, game_id) -> Game:
        key = f"hanabi:game:{game_id}"
        raw = self._retry(lambda: self.redis.get(key))

        if not raw:
            return None

        data = json.loads(raw)
        return Game.from_dict(data)

    def save_game(self,game: Game):
        key = f"hanabi:game:{game.gameID}"
        payload = json.dumps(game.to_dict())
        self._retry(lambda: self.redis.set(key, payload)) # pass state dict or Game object in interface
        
        
    def load_user(self, username):
        key = f"hanabi:user:{username}"
        raw = self._retry(lambda: self.redis.get(key))
        return json.loads(raw) if raw else None
    
    def save_user(self, user):
        key = f"hanabi:user:{user._username}"
        payload = json.dumps({
            "fullName": user._fullName,
            "email": user._email,
            "password": user._hashedPass
        })
        self._retry(lambda: self.redis.set(key, payload))
    
    def load_lobby(self, lobby_id):
        pass
    
    def save_lobby(self, lobby):
        pass