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

class ILobbyRepository(ABC):
    @abstractmethod
    def load_lobby(self, lobby_id):
        pass
    @abstractmethod
    def save_lobby(self, lobby):
        pass
