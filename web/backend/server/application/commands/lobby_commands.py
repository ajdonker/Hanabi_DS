from database import RedisRepository
from server.application.commands.commands import Command
from server.domain.exceptions import LobbyException
from server.presentation.websocket_handler import Event
from server.application.waitingPlayer import WaitingPlayer
from server.application.matchmakingService import MatchmakingService

class CreateLobbyCommand(Command):

    def __init__(self, matchmaking_service: MatchmakingService):
        self.matchmaking_service = matchmaking_service

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

    def __init__(self, matchmaking_service: MatchmakingService):
        self.matchmaking_service = matchmaking_service
        
    def execute(self, data) -> list[Event]:

        lobbyID = data["lobby_id"]
        userJoined = data["user_joined"]
        playerID = data["player_id"]
        
        events = []

        player = WaitingPlayer(playerID, userJoined, lobbyID)
        
        try :
            result = self.matchmaking_service.join_lobby(lobbyID, player)
        except LobbyException :
            return Event("error", {"message" : "Lobby not found"})
        
        events.append(Event("user_joined", {"lobby_id": lobbyID, "user_joined" : userJoined}))
        
        if(result == "WAITING") :
            events.append(Event("lobby_waiting", {"lobby_id": lobbyID}))
        elif(result == "GAME_CREATED") :
            events.append(Event("game_created", {"lobby_id": lobbyID}))

        return events
