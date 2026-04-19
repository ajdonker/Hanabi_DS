import pytest

from server.application.command_dispatcher import CommandDispatcher


class DummyCommand:
    pass


class DummyHandler:
    def execute(self, command):
        return ["ok"]


def test_dispatches_to_matching_handler():
    dispatcher = CommandDispatcher({
        DummyCommand: DummyHandler()
    })

    result = dispatcher.dispatch(DummyCommand())

    assert result == ["ok"]


def test_unknown_command_type_raises():
    dispatcher = CommandDispatcher({})

    with pytest.raises(ValueError):
        dispatcher.dispatch(DummyCommand())