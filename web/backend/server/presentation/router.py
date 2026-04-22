from fastapi import APIRouter, WebSocket
from server.presentation.connection_manager import ConnectionManager
from server.presentation.websocket_handler import WebSocketHandler
from server.application.command_dispatcher import CommandDispatcher
from database.RedisRepository import RedisRepository
from server.application.commands.game_commands import PlayCardCommand,DiscardCardCommand,GiveHintCommand
from server.application.commands.auth_commands import RegisterCommand,LoginCommand
from server.application.commands.lobby_commands import CreateLobbyCommand,JoinLobbyCommand
from server.application.handlers.game_command_handlers import PlayCardHandler, GiveHintHandler, DiscardCardHandler
from server.application.handlers.auth_handlers import RegisterHandler,LoginHandler
from server.application.handlers.lobby_command_handlers import CreateLobbyHandler,JoinLobbyHandler
from server.presentation.command_factory import CommandFactory
from server.application.matchmakingService import MatchmakingService

ws_router = APIRouter()

matchmaking_service = MatchmakingService()
_connection_manager = ConnectionManager()
_command_factory = CommandFactory()

@ws_router.websocket("/ws")
async def ws_endpoint(websocket: WebSocket) -> None:
    repo = websocket.app.state.repo 
    
    _dispatcher = CommandDispatcher({
        PlayCardCommand: PlayCardHandler(repo),
        DiscardCardCommand: DiscardCardHandler(repo),
        GiveHintCommand: GiveHintHandler(repo),

        RegisterCommand: RegisterHandler(repo),
        LoginCommand: LoginHandler(repo),

        CreateLobbyCommand: CreateLobbyHandler(matchmaking_service),
        JoinLobbyCommand: JoinLobbyHandler(matchmaking_service),
    })
    
    _websocket_handler = WebSocketHandler(
        connection_manager=_connection_manager,
        dispatcher= _dispatcher,
        command_factory= _command_factory
    )

    
    await _websocket_handler.main(websocket)
