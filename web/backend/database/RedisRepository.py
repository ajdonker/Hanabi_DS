from database.gameSerializer import GameSerializer
from database.repos import IGameRepository, IUserRepository
from server.application import user
from server.application.user import User
from server.domain.game import Game
from server.application.gameInformation import GameInformation
from redis.sentinel import Sentinel
import json, time, random, os
class RedisRepository(IGameRepository, IUserRepository):
    '''Stores game states per game_id and game session related metadata - player -> game, game -> players, game ->server'''
    def __init__(self, redis_client=None):
        if redis_client:
            self.redis = redis_client
        else:
            sentinel_nodes = os.getenv("SENTINEL_NODES", "localhost:26379").split(",")
            sentinel = Sentinel([tuple(node.split(":")) for node in sentinel_nodes])

            self.redis = sentinel.master_for(
                os.getenv("SENTINEL_MASTER_NAME", "mymaster"),
                decode_responses=True
            )
        

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
    
    def load_game(self, game_id) -> Game | None:
        key = f"hanabi:game:{game_id}"
        
        raw = self._retry(lambda: self.redis.get(key))

        if not raw:
            return None

        data = json.loads(raw)
        
        return GameSerializer.from_dict(data)

    def save_game(self,game: Game):
        if not hasattr(game, "gameID"):
            raise TypeError(f"Expected Game object, got {type(game)}")

        key = f"hanabi:game:{game.gameID}"
        
        payload = json.dumps(GameSerializer.to_dict(game))
        
        self._retry(lambda: self.redis.set(key, payload)) 

    def save_game_information(self,game_info: GameInformation):
        key = f"hanabi:game_info:{game_info.game_id}"
    
        payload = json.dumps({
            "players": [p.name for p in game_info.players],
            "container": game_info.container_name,
            "timestamp": game_info.timestamp,
        })

        self._retry(lambda: self.redis.set(key, payload))
             
    def load_user(self, username : str) -> User | None:
        key = f"hanabi:user:{username}"
        
        raw = self._retry(lambda: self.redis.get(key))
    
        if not raw:
            return None
    
        data = json.loads(raw)
       
        return User.from_dict(data, username)
    
    def save_user(self, user : User):
        key = f"hanabi:user:{user._username}"
        
        payload = json.dumps(User.to_dict(user))
        
        self._retry(lambda: self.redis.set(key, payload))
