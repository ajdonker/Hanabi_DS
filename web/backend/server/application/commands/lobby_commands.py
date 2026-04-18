from server.application.commands.commands import Command
from server.application import lobbyInitializer
from server.presentation.websocket_handler import Event
from server.application.waitingPlayer import WaitingPlayer
from server.application.matchmakingService import MatchmakingService
from server.domain.exceptions import LobbyException
class CreateLobbyCommand(Command):

    def __init__(self, matchmaking_service: MatchmakingService):
        self.matchmaking_service = matchmaking_service

    def execute(self, message):

        userCreator = message["user_creator"]
        lobbyID = message["lobby_id"]
        maxUsers = message["maxUsers"]

        player = WaitingPlayer(player_id= generate_id(), name = userCreator)

        try :
            result = self.matchmaking_service.create_lobby(lobbyID, maxUsers,player)
        except LobbyException :
            return Event("error", {"message" : "Lobby already exist"})

        return Event(result, {"lobby_id": lobbyID})

#example of JSON request to join a lobby:
# { lobby_id: "lobby1", 
#   user_joined: "bob"
# }

class JoinLobbyCommand(Command):

    def __init__(self, matchmaking_service: MatchmakingService):
        self.matchmaking_service = matchmaking_service

    def execute(self, message):

        lobbyID = message["lobby_id"]
        userJoined = message["user_joined"]

        events = []

        player = WaitingPlayer(player_id=generate_id(), name = userJoined)

        try :
            result = self.matchmaking_service.join_lobby(lobbyID,player)
        except LobbyException :
            return Event("error", {"message" : "Lobby not found"})

        events.append(Event("user_joined", {"lobby_id": lobbyID, "user_joined" : userJoined}))

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