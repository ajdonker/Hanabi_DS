from server.application.handlers.handler import IHandler
from server.events import Event

class CommandDispatcher:
    def __init__(self, command_handlers: dict[type, IHandler]):
        self.command_handlers = command_handlers

    def dispatch(self, command) -> list[Event]:
        handler = self.command_handlers.get(type(command))
        if handler is None:
            raise ValueError(f"No handler found for command type: {type(command)}")
        return handler.execute(command)
