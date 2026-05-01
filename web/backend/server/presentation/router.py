from fastapi import APIRouter, WebSocket
import os
from server.presentation.connection_manager import ConnectionManager
from server.presentation.websocket_handler import WebSocketHandler
from server.application.command_dispatcher import CommandDispatcher
from database.RedisRepository import RedisRepository
from server.application.commands.game_commands import PlayCardCommand,DiscardCardCommand,GiveHintCommand,GetGameStateCommand
from server.application.commands.auth_commands import RegisterCommand,LoginCommand
from server.application.commands.lobby_commands import CreateLobbyCommand,JoinLobbyCommand,ListLobbiesCommand,LobbyDetailCommand
from server.application.handlers.game_command_handlers import PlayCardHandler, GiveHintHandler, DiscardCardHandler, GetGameStateHandler
from server.application.handlers.auth_handlers import RegisterHandler,LoginHandler
from server.application.handlers.lobby_command_handlers import CreateLobbyHandler,JoinLobbyHandler,ListLobbiesHandler,LobbyDetailHandler
from server.presentation.command_factory import CommandFactory
from server.application.matchmakingService import MatchmakingService

ws_router = APIRouter()

_connection_manager = ConnectionManager()
_command_factory = CommandFactory()
IS_GAME_SERVER = os.getenv("IS_GAME_SERVER") == "1" or os.getenv("GAME_ID") is not None
# Only the main backend should create MatchmakingService,
# because MatchmakingService creates GameServerManager, which needs Docker socket.
matchmaking_service = None if IS_GAME_SERVER else MatchmakingService()
@ws_router.websocket("/ws")
async def ws_endpoint(websocket: WebSocket) -> None:
    repo = websocket.app.state.repo 
    
    command_handlers = {
        PlayCardCommand: PlayCardHandler(repo),
        DiscardCardCommand: DiscardCardHandler(repo),
        GiveHintCommand: GiveHintHandler(repo),
        GetGameStateCommand: GetGameStateHandler(repo),

        RegisterCommand: RegisterHandler(repo),
        LoginCommand: LoginHandler(repo),
    }

    # Add lobby handlers ONLY in the main backend container.
    if matchmaking_service is not None:
        command_handlers[CreateLobbyCommand] = CreateLobbyHandler(matchmaking_service)
        command_handlers[JoinLobbyCommand] = JoinLobbyHandler(matchmaking_service)
        command_handlers[ListLobbiesCommand] = ListLobbiesHandler(matchmaking_service)
        command_handlers[LobbyDetailCommand] = LobbyDetailHandler(matchmaking_service)
        
    _dispatcher = CommandDispatcher(command_handlers)

    _websocket_handler = WebSocketHandler(
        connection_manager=_connection_manager,
        dispatcher=_dispatcher,
        command_factory=_command_factory,
    )

    
    await _websocket_handler.main(websocket)
