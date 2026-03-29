from abc import ABC, abstractmethod
import time

class IUserRepository(ABC):
    @abstractmethod
    def load_user(self, username):
        pass
    @abstractmethod
    def save_user(self, user):
        pass

class IGameRepository(ABC):
    @abstractmethod
    def load_game(self, game_id):
        pass
    @abstractmethod
    def save_game(self, game_id, state_dict):
        pass

    @abstractmethod
    def save_player_game_mapping(self, player, game_id):
        pass

    @abstractmethod
    def get_game_id_for_player(self, player):
        pass

    @abstractmethod
    def save_game_players(self, game_id, players):
        pass

    @abstractmethod
    def get_game_players(self, game_id):
        pass

    @abstractmethod
    def save_server_info(self, game_id, server_info):
        pass

    @abstractmethod
    def get_server_info(self, game_id):
        pass

    @abstractmethod
    def clear_server_info(self, game_id):
        pass

class RedisRepositoryBase:
    def __init__(self, redis_client, redis_factory):
        self.redis = redis_client
        self.redis_factory = redis_factory
    
    def _retry(self,func,retries = 3,delay = 0.5):
        for attempt in range(retries):
            try:
                return func()
            except Exception as e:
                print(f"[WARN] redis op failed {attempt+1}/{retries}: {e}", flush=True)
                self.redis = self.redis_factory()
                time.sleep(delay)
        raise RuntimeError("Redis operation failed")
    

class FakeGameRepository(IGameRepository):
    def __init__(self):
        self.games = {}
        self.player_to_game = {}
        self.game_players = {}
        self.server_info = {}

    def load_game(self, game_id):
        return self.games.get(game_id)

    def save_game(self, game_id, state_dict):
        self.games[game_id] = state_dict

    def save_player_game_mapping(self, player, game_id):
        self.player_to_game[player] = game_id

    def get_game_id_for_player(self, player):
        return self.player_to_game.get(player)

    def save_game_players(self, game_id, players):
        self.game_players[game_id] = players

    def get_game_players(self, game_id):
        return self.game_players.get(game_id)

    def save_server_info(self, game_id, server_info):
        self.server_info[game_id] = server_info

    def get_server_info(self, game_id):
        return self.server_info.get(game_id)

    def clear_server_info(self, game_id):
        self.server_info.pop(game_id, None)