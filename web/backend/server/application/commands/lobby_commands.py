from server.application import lobbyInitializer
from server.events import Event
from server.application.waitingPlayer import WaitingPlayer
from server.application.matchmakingService import MatchmakingService

class CreateLobbyCommand():
    def __init__(self, lobby_id: str, max_users: int, user_creator: str):
        self.lobby_id = lobby_id
        self.max_users = max_users
        self.user_creator = user_creator


class JoinLobbyCommand():
    def __init__(self, lobby_id: str, user_joined: str):
        self.lobby_id = lobby_id
        self.user_joined = user_joined