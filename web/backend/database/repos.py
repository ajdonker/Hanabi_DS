from abc import ABC, abstractmethod

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
    def save_game(self, game):
        pass

class IMatchmakerRepository(ABC):

    # --- PLAYER ↔ GAME ---
    @abstractmethod
    def save_player_game(self, player_id: str, game_id: str):
        pass
    
    @abstractmethod
    def get_game_by_player(self, player_id: str) -> str | None:
        pass
    
    @abstractmethod
    def remove_player(self, player_id: str):
        pass

    # --- GAME → SERVER INFO ---
    @abstractmethod
    def save_game_server(self, game_id: str, host: str, port: int, container: str):
        pass
    
    @abstractmethod
    def get_server_by_game(self, game_id: str) -> dict | None:
        pass
    
    @abstractmethod
    def remove_game(self, game_id: str):
        pass
