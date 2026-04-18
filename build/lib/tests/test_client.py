import json 
from tests.dummyclasses import DummyConn, DummyDB, DummyFile
from client.client import Client
import pytest

def test_process_command_play():
    c = Client("alice")
    c.idx = 0

    msg = c.process_command("PLAY 2")

    assert msg == {
        "type": "PLAY",
        "player_idx": 0,
        "card_idx": 2
    }


def test_process_command_disc():
    c = Client("alice")
    c.idx = 1

    msg = c.process_command("DISC 3")

    assert msg == {
        "type": "DISC",
        "player_idx": 1,
        "card_idx": 3
    }


def test_process_command_hint_number():
    c = Client("alice")
    c.idx = 0

    msg = c.process_command("HINT 1 5")

    assert msg == {
        "type": "HINT",
        "from": 0,
        "to": 1,
        "number": 5
    }


def test_process_command_hint_color():
    c = Client("alice")
    c.idx = 0

    msg = c.process_command("HINT 1 red")

    assert msg == {
        "type": "HINT",
        "from": 0,
        "to": 1,
        "color": "RED"
    }


def test_process_command_empty_raises():
    c = Client("alice")
    c.idx = 0

    with pytest.raises(ValueError, match="Empty command"):
        c.process_command("   ")


def test_process_command_unknown_raises():
    c = Client("alice")
    c.idx = 0

    with pytest.raises(ValueError, match="Unknown command"):
        c.process_command("JUMP 2")


def test_process_command_bad_play_raises():
    c = Client("alice")
    c.idx = 0

    with pytest.raises(ValueError, match="Usage: PLAY"):
        c.process_command("PLAY x")


def test_process_command_bad_hint_target_raises():
    c = Client("alice")
    c.idx = 0

    with pytest.raises(ValueError, match="Second argument must be the target player index"):
        c.process_command("HINT bob red")


def test_process_server_message_assign_idx():
    c = Client("alice")

    c.process_server_message({"type": "ASSIGN_IDX", "idx": 1})

    assert c.idx == 1


def test_process_server_message_state_starts_game():
    c = Client("alice")

    state_msg = {
        "type": "STATE",
        "board": {},
        "tokens": 8,
        "misfires": 0,
        "hands": [],
        "current_turn": 0
    }

    c.process_server_message(state_msg)

    assert c.game_started is True
    assert c.current_turn == 0
    assert c.last_state == state_msg


def test_get_startup_assignment_prefers_resume():
    c = Client("alice")

    expected = {
        "type": "MATCH_FOUND",
        "game_id": "g1",
        "host": "127.0.0.1",
        "port": 12345
    }

    c.try_resume_by_player = lambda _: expected
    c.get_match_assignment = lambda _: {"type": "MATCH_FOUND", "game_id": "wrong", "host": "x", "port": 1}

    result = c.get_startup_assignment("alice")

    assert result == expected
    assert c.game_id == "g1"


def test_get_startup_assignment_falls_back_to_queue():
    c = Client("alice")

    expected = {
        "type": "MATCH_FOUND",
        "game_id": "g2",
        "host": "127.0.0.1",
        "port": 12345
    }

    def fail_resume(name):
        raise Exception("no active game")

    c.try_resume_by_player = fail_resume
    c.get_match_assignment = lambda _: expected

    result = c.get_startup_assignment("alice")

    assert result == expected
    assert c.game_id == "g2"


def test_handle_disconnect_reconnects():
    c = Client("alice")
    c.game_id = "g1"

    called = {}

    class DummySockFile:
        def close(self):
            called["sock_file_closed"] = True

    class DummySock:
        def close(self):
            called["sock_closed"] = True

    c.sock_file = DummySockFile()
    c.sock = DummySock()

    c.get_game_location = lambda name, game_id: {
        "type": "MATCH_FOUND",
        "game_id": "g1",
        "host": "127.0.0.1",
        "port": 9999
    }

    def fake_connect(host, port, game_id, name):
        called["connect"] = (host, port, game_id, name)

    c.connect_to_game_server = fake_connect

    c.handle_disconnect()

    assert called["sock_file_closed"] is True
    assert called["sock_closed"] is True
    assert called["connect"] == ("127.0.0.1", 9999, "g1", "alice")