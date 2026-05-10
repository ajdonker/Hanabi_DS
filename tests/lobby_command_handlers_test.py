from server.application.commands.lobby_commands import CreateLobbyCommand, JoinLobbyCommand
from server.application.handlers import lobby_command_handlers
from server.application.handlers.lobby_command_handlers import CreateLobbyHandler, JoinLobbyHandler
from server.presentation.command_factory import CommandFactory
from server.presentation.command_message import CommandMessage


class FakeRepo:
    def __init__(self, game_id=None):
        self.game_id = game_id

    def get_player_game_mapping(self, player_name):
        return self.game_id


class FakeMatchmakingService:
    def __init__(self, game_id=None):
        self.repo = FakeRepo(game_id)
        self.lobbies = {}
        self.created_lobbies = []
        self.joined_lobbies = []

    def create_lobby(self, lobby_id, max_users, user_creator):
        self.created_lobbies.append((lobby_id, max_users, user_creator))
        self.lobbies[lobby_id] = {
            "players": [user_creator],
            "max_users": max_users,
        }
        return "LOBBY_CREATED"

    def join_lobby(self, lobby_id, player):
        self.joined_lobbies.append((lobby_id, player))
        return "WAITING"


def test_command_factory_create_lobby_does_not_require_frontend_lobby_id():
    command = CommandFactory().create(CommandMessage(
        type="command",
        action="lobby.create",
        data={
            "maxUsers": 3,
            "userCreator": "alice",
        },
    ))

    assert isinstance(command, CreateLobbyCommand)
    assert command.max_users == 3
    assert command.user_creator == "alice"
    assert not hasattr(command, "lobby_id")



def test_create_lobby_forbidden_when_player_has_unfinished_game():
    matchmaking_service = FakeMatchmakingService(game_id="g1")
    handler = CreateLobbyHandler(matchmaking_service)

    events = handler.execute(CreateLobbyCommand(max_users=2, user_creator="alice"))

    assert events[0].event == "error"
    assert events[0].data == {
        "message": "Player is already playing an unfinished game",
        "gameId": "g1",
    }
    assert matchmaking_service.created_lobbies == []


def test_join_lobby_forbidden_when_player_has_unfinished_game():
    matchmaking_service = FakeMatchmakingService(game_id="g1")
    handler = JoinLobbyHandler(matchmaking_service)

    events = handler.execute(JoinLobbyCommand("l1", "alice"))

    assert events[0].event == "error"
    assert events[0].data == {
        "message": "Player is already playing an unfinished game",
        "gameId": "g1",
    }
    assert matchmaking_service.joined_lobbies == []


def test_join_lobby_allowed_when_player_has_no_unfinished_game():
    matchmaking_service = FakeMatchmakingService()
    handler = JoinLobbyHandler(matchmaking_service)

    events = handler.execute(JoinLobbyCommand("l1", "alice"))

    assert events[0].event == "WAITING"
    assert len(matchmaking_service.joined_lobbies) == 1
