from commands import Command
from database.repos import RedisRepository
from application import lobbyInitializer
from presentation import Event
from web.backend.server.application.matchmakingService import MatchmakingService

class CreateLobbyCommand(Command):
    
    def __init__(self, lobby_repository, lobby_initializer):
        self.lobby_repository = lobby_repository
        self.lobby_initializer = lobby_initializer

    def execute(self, message):

        lobby = self.lobby_initializer.create_lobby(
            message.name,
            message.max_users
        )
        self.lobby_repository.save(lobby)
        return Event("LOBBY_CREATED", {"lobby_id": lobby.name})


class JoinLobbyCommand(Command):

    def __init__(self, lobby_repository, lobby_initializer, matchmaking_service):
        self.lobby_repository = lobby_repository
        self.lobby_initializer = lobby_initializer
        self.matchmaking_service = MatchmakingService()

    def execute(self, message):

        lobby = self.lobby_repository.load(message.lobby_id)

        self.lobby_initializer.add_player(lobby, message.player)

        self.lobby_repository.save(lobby)

        if not lobby.is_full():
            return Event("WAITING_FOR_PLAYERS", {"lobby_id": lobby.name})

        self.matchmaking_service.create_game(lobby)

        return ##