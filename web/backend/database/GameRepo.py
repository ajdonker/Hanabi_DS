from database.repos import IGameRepository, ILobbyRepository, IUserRepository
import json
# At any moment, there should be only one active authoritative server for a given game_id.
class RedisRepository(IGameRepository, ILobbyRepository, IUserRepository):
    '''Stores game states per game_id and game session related metadata - player -> game, game -> players, game ->server'''
    def __init__(self, redis_client):
        self.redis = redis_client

    def _retry(self, fn, retries=3):
        for _ in range(retries):
            try:
                return fn()
            except Exception:
                continue
        raise RuntimeError("Redis operation failed")
    
    def load_game(self, game_id):
        key = f"hanabi:game:{game_id}"
        raw = self._retry(lambda: self.redis.get(key))
        return json.loads(raw) if raw else None

    def save_game(self, game_id, state_dict):
        key = f"hanabi:game:{game_id}"
        payload = json.dumps(state_dict)
        self._retry(lambda: self.redis.set(key, payload))
        
    def load_user(self, username):
        key = f"hanabi:user:{username}"
        raw = self._retry(lambda: self.redis.get(key))
        return json.loads(raw) if raw else None
    
    def save_user(self, user):
        key = f"hanabi:user:{user.username}"
        payload = json.dumps({
            "fullName": user.fullName,
            "email": user.email,
            "password": user._hashedPass
        })
        self._retry(lambda: self.redis.set(key, payload))
    
