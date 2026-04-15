from database.gameSerializer import GameSerializer
from database.repos import IGameRepository, IMatchmakerRepository, IUserRepository
from server.application import user
from server.application.user import User
from server.domain.game import Game
import json, time, random
class RedisRepository(IGameRepository, IMatchmakerRepository, IUserRepository):
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

    ## ------------------------------------------------ GameRepository ------------------------------------------------
    def load_game(self, game_id : str) -> Game | None:
        key = f"hanabi:game:{game_id}"
        
        raw = self._retry(lambda: self.redis.get(key))

        if not raw:
            return None

        data = json.loads(raw)
        
        return GameSerializer.from_dict(data)

    def save_game(self,game: Game):
        key = f"hanabi:game:{game.gameID}"
        
        payload = json.dumps(GameSerializer.to_dict(game))
        
        self._retry(lambda: self.redis.set(key, payload)) # pass state dict or Game object in interface
    
    #--------------------------------------------------------------------------------------------------------------------
    #------------------------------------------------ UserRepository ----------------------------------------------------

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
    
    ## -----------------------------------------------------------------------------------------------------------------
    ## ------------------------------------------------ MatchmakerRepository ------------------------------------------------
    
    # Mapping player <-> game
    
    def save_player_game(self, username: str, game_id: str):
        key = f"hanabi:match:{username}"
        
        payload = game_id
        
        self._retry(lambda: self.redis.set(key, payload))
    
    def get_game_by_player(self, username: str) -> str | None:
        key = f"hanabi:match:{username}"
        
        game_id  = self._retry(lambda: self.redis.get(key))
    
        if not game_id:
            return None
    
        return game_id
    
    def remove_player(self, player_id: str):
        pass

    # --- GAME → SERVER INFO ---
    def save_game_server(self, game_id: str, host: str, port: int, container: str):
        pass
    
    def get_server_by_game(self, game_id: str) -> dict | None:
        pass
    
    def remove_game(self, game_id: str):
        pass
