class CommmandDispatcher:
    def __init__(self, command_handlers):
        self.command_handlers = command_handlers

    def dispatch(self, command):
        handler = self.command_handlers.get(type(command))
        if handler is None:
            raise ValueError(f"No handler found for command type: {type(command)}")
        return handler.handle(command)
