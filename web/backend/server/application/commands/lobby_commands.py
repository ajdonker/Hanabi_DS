from commands import Command
from database.repos import RedisRepository
from application import lobbyInitializer
from presentation import Event
from web.backend.server.application.waitingPlayer import WaitingPlayer
from web.backend.server.application.matchmakingService import MatchmakingService


#example of JSON request to create a lobby:
# { lobby_id: "lobby1", 
#   max_users: 4,
#   user_creator: "alice" 
# }

class CreateLobbyCommand(Command):

    def __init__(self, matchmaking_service):
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

    def __init__(self, matchmaking_service):
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