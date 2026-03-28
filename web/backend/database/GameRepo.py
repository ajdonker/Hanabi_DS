from database.repos import IGameRepository,RedisRepositoryBase
import json
# At any moment, there should be only one active authoritative server for a given game_id.
class RedisGameRepository(IGameRepository,RedisRepositoryBase):
    '''Stores game states per game_id and game session related metadata - player -> game, game -> players, game ->server'''
    def __init__(self, redis_client, redis_factory):
        self.redis = redis_client
        self.redis_factory = redis_factory

    def load_game(self, game_id):
        key = f"hanabi:game:{game_id}"
        raw = self._retry(lambda: self.redis.get(key))
        return json.loads(raw) if raw else None

    def save_game(self, game_id, state_dict):
        key = f"hanabi:game:{game_id}"
        payload = json.dumps(state_dict)
        self._retry(lambda: self.redis.set(key, payload))

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