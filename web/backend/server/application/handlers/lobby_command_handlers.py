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


def generate_lobby_id(matchmaking_service: MatchmakingService) -> str:
    while True:
        lobby_id = generate_id()
        if lobby_id not in matchmaking_service.lobbies:
            return lobby_id


def find_unfinished_game_id(matchmaking_service: MatchmakingService, player_name: str) -> str | None:
    return matchmaking_service.repo.get_player_game_mapping(player_name)


def player_already_playing_event(game_id: str) -> Event:
    return Event("error", {
        "message": "Player is already playing an unfinished game",
        "gameId": game_id,
    })


class CreateLobbyHandler:
    def __init__(self, matchmaking_service: MatchmakingService):
        self.matchmaking_service = matchmaking_service

    def execute(self, command: CreateLobbyCommand) -> list[Event]:
        game_id = find_unfinished_game_id(
            self.matchmaking_service,
            command.user_creator,
        )
        if game_id:
            return [player_already_playing_event(game_id)]

        lobby_id = generate_lobby_id(self.matchmaking_service)
        player = WaitingPlayer(
            player_id=generate_id(),
            name=command.user_creator,
            lobby_id=lobby_id,
        )

        self.matchmaking_service.create_lobby(
            lobby_id,
            command.max_users,
            player.name,
        )

        return [Event("lobby_created", {
            "lobbyId": lobby_id,
            "name": f"Game {lobby_id}",
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
        game_id = find_unfinished_game_id(
            self.matchmaking_service,
            command.user_joined,
        )
        if game_id:
            return [player_already_playing_event(game_id)]

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
