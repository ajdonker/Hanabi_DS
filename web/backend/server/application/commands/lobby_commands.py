from server.application.commands.commands import Command
from server.application import lobbyInitializer
from server.presentation.websocket_handler import Event
from server.application.waitingPlayer import WaitingPlayer
from server.application.matchmakingService import MatchmakingService

class CreateLobbyCommand(Command):

    def __init__(self, matchmaking_service: MatchmakingService):
        self.matchmaking_service = matchmaking_service

    def execute(self, message):

        player = WaitingPlayer(player_id= generate_id(), name = message.user_creator)

        self.matchmaking_service.create_lobby(
            message.lobby_id,
            message.max_users,
            player
        )

        return Event("LOBBY_CREATED", {"lobby_id": message.lobby_id})

#example of JSON request to join a lobby:
# { lobby_id: "lobby1", 
#   user_joined: "bob"
# }

class JoinLobbyCommand(Command):

    def __init__(self, matchmaking_service: MatchmakingService):
        self.matchmaking_service = matchmaking_service

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