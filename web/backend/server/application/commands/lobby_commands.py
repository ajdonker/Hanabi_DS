from commands import Command
from database.repos import RedisRepository
from application import lobbyInitializer
from presentation import Event
from web.backend.matchmaker.matchmaker import WaitingPlayer

class CreateLobbyCommand(Command):

    def __init__(self, matchmaking_service):
        self.matchmaking_service = matchmaking_service

    def execute(self, message):

        player = WaitingPlayer(
            player_id=message.player_id,
            name=message.user_creator
        )

        self.matchmaking_service.setLobbySize(message.lobby_size)
        result = self.matchmaking_service.add_player_to_pool(player)

        return self._map_result(result)

    def _map_result(self, result):
        if result == "WAITING":
            return Event("WAITING_FOR_PLAYERS", {})
        elif result == "MATCH_FOUND":
            return Event("MATCH_FOUND", {
                "game_id": result.game_info.game_id
            })

class JoinLobbyCommand(Command):

    def __init__(self, matchmaking_service):
        self.matchmaking_service = matchmaking_service

    def execute(self, message):

        player = WaitingPlayer(
            player_id=message.player_id,
            name=message.user_joined
        )

        result = self.matchmaking_service.add_player_to_pool(player)

        return self._map_result(result)

    def _map_result(self, result):
        if result.status == "WAITING":
            return Event("WAITING_FOR_PLAYERS", {})
        elif result.status == "MATCH_FOUND":
            return Event("MATCH_FOUND", {
                "game_id": result.game_info.game_id
            })
        
#can be refactored as a single command with a parameter for create/join,
#but protocol must be updated accordingly and also at presentation layer and frontend