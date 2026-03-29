from typing import Protocol

from web.backend.server.application.models import CommandError, CommandMessage, Event


class CommandHandler(Protocol):
    def execute(self, message: CommandMessage) -> list[Event]:
        ...


class CommandDispatcher:
    def __init__(self, handlers: dict[str, CommandHandler]) -> None:
        self.handlers = handlers

    def dispatch(self, message: CommandMessage) -> list[Event]:
        if message.type != "command":
            raise CommandError("Unsupported message type.", details={"type": message.type})

        handler = self.handlers.get(message.action)
        if handler is None:
            raise CommandError("Unknown action.", details={"action": message.action})

        return handler.execute(message)
