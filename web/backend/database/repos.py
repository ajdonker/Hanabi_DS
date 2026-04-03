from abc import ABC, abstractmethod
import time
from web.backend.server.domain.game import Game
from web.backend.server.application.user import User

class IUserRepository(ABC):
    @abstractmethod
    def load_user(self, username) -> User | None:
        pass
    @abstractmethod
    def save_user(self, user: User):
        pass

class IGameRepository(ABC):
    @abstractmethod
    def load_game(self, game_id: str) -> Game | None:
        pass
    @abstractmethod
    def save_game(self, game: Game):
        pass

    
'''todo
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
'''