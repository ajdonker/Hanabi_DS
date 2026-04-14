from database import RedisRepository
from server.application.commands.commands import Command
from server.domain.exceptions import LobbyException
from server.presentation.websocket_handler import Event
from server.application.waitingPlayer import WaitingPlayer
from server.application.matchmakingService import MatchmakingService

class CreateLobbyCommand(Command):

    def __init__(self, matchmaking_service: MatchmakingService, repository = None):
        self.matchmaking_service = matchmaking_service
        self.matchmakerRepository = repository or RedisRepository()

    def execute(self, data):

        userCreator = data["user_creator"]
        lobbyID = data["lobby_id"]
        maxUsers = data["maxUsers"]

        try :
            self.matchmaking_service.create_lobby(lobbyID, maxUsers, userCreator)
        except LobbyException :
            return Event("error", {"message" : "Lobby already created"})
        
        return Event("lobby_created", {"lobby_id": lobbyID})

#example of JSON request to join a lobby:
# { 
#   lobby_id: "lobby1", 
#   user_joined: "bob"
# }

class JoinLobbyCommand(Command):

    def __init__(self, matchmaking_service: MatchmakingService, repository = None):
        self.matchmaking_service = matchmaking_service
        self.matchmakerRepository = repository or RedisRepository()
        
    def execute(self, message):

        player = WaitingPlayer(player_id=generate_id(), name=message.user_joined)

        result = self.matchmaking_service.join_lobby(
            message.lobby_id,
            player
        )

        if result == "WAITING":
            return Event(result, {})

        elif result == "MATCH_FOUND":
            return Event(result, {
                "game_id": result.game_id,
                "host": result.host,
                "port": result.port
            })
        else :
            pass #unknown error

def generate_id():
    import uuid
    return str(uuid.uuid4())[:8]