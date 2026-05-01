from database.repos import IGameRepository
from server.events import Event
from.handler import IHandler
from server.domain.exceptions import *
from server.domain.exceptionMapper import ExceptionMapper
from server.application.commands.lobby_commands import CreateLobbyCommand,JoinLobbyCommand,ListLobbiesCommand,LobbyDetailCommand
import uuid
from server.application.waitingPlayer import WaitingPlayer
from server.application.matchmakingService import MatchmakingService

def generate_id():
    return str(uuid.uuid4())[:8]


class CreateLobbyHandler:
    def __init__(self, matchmaking_service: MatchmakingService):
        self.matchmaking_service = matchmaking_service

    def execute(self, command: CreateLobbyCommand) -> list[Event]:
        player = WaitingPlayer(
            player_id=generate_id(),
            name=command.user_creator,
            lobby_id=command.lobby_id,
        )

        self.matchmaking_service.create_lobby(
            command.lobby_id,
            command.max_users,
            player.name,   # or player, depending on your actual create_lobby signature
        )

        return [Event("lobby_created", {
            "lobbyId": command.lobby_id,
            "name": f"Game {command.lobby_id}",
            "maxUser": command.max_users,
            "numUser": 1,
            "currentUsers": [player.name],
        })]


class ListLobbiesHandler:
    def __init__(self, matchmaking_service: MatchmakingService):
        self.matchmaking_service = matchmaking_service

    def execute(self, command: ListLobbiesCommand) -> list[Event]:
        return [Event("lobby_list", {
            "lobbies": self.matchmaking_service.list_lobbies()
        })]


class LobbyDetailHandler:
    def __init__(self, matchmaking_service: MatchmakingService):
        self.matchmaking_service = matchmaking_service

    def execute(self, command: LobbyDetailCommand) -> list[Event]:
        detail = self.matchmaking_service.get_lobby_detail(
            command.lobby_id,
            command.player_name,
        )
        if detail is None:
            return [Event("error", {"message": "Lobby does not exist"})]

        if detail["status"] == "MATCH_FOUND":
            return [Event("MATCH_FOUND", {
                "game_id": detail["game_id"],
                "host": detail["host"],
                "port": detail["port"],
            })]

        return [Event("lobby_detail", detail)]


class JoinLobbyHandler:
    def __init__(self, matchmaking_service: MatchmakingService):
        self.matchmaking_service = matchmaking_service

    def execute(self, command: JoinLobbyCommand) -> list[Event]:
        player = WaitingPlayer(
            player_id=generate_id(),
            name=command.user_joined,
            lobby_id=command.lobby_id,
        )

        result = self.matchmaking_service.join_lobby(
            command.lobby_id,
            player
        )

        if result == "WAITING":
            return [Event("WAITING", {})]

        if result == "MATCH_FOUND":
            game = self.matchmaking_service.find_game_by_player(command.user_joined)
            if game is None:
                return [Event("error", {"message": "Match found but game not found"})]

            return [Event("MATCH_FOUND", {
                "game_id": game.game_id,
                "host": game.host,
                "port": game.port
            })]
        return [Event("error", {"message": "Unknown matchmaking result"})]
