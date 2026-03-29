from web.backend.server.application.commands import Login
from web.backend.server.application.dispatcher import CommandDispatcher


def build_command_dispatcher() -> CommandDispatcher:
    login = Login()
    handlers = {
        "player.login": login,
    }
    return CommandDispatcher(handlers=handlers)
