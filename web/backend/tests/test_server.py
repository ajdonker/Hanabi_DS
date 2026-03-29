import json
from tests.dummyclasses import DummyConn,DummyFile,DummyRepo
from server.server import Server

def parse_last_json(conn: DummyConn):
    assert conn.sent, "No messages sent"
    return json.loads(conn.sent[-1].strip())


def parse_all_json(conn: DummyConn):
    return [json.loads(m.strip()) for m in conn.sent]

def test_join_wrong_game_id():
    repo = DummyRepo()
    server = Server("g1", ["a", "b"], repo)
    conn = DummyConn()

    ok = server.handle_join_message(
        {"player": "a", "game_id": "wrong"},
        conn,
        ("127.0.0.1", 1111),
    )

    assert ok is False
    msg = parse_last_json(conn)
    assert msg["type"] == "ERROR"
    assert msg["msg"] == "Wrong game_id"
    assert conn.closed is True


def test_join_player_not_allowed():
    repo = DummyRepo()
    server = Server("g1", ["a", "b"], repo)
    conn = DummyConn()

    ok = server.handle_join_message(
        {"player": "x", "game_id": "g1"},
        conn,
        ("127.0.0.1", 1111),
    )

    assert ok is False
    msg = parse_last_json(conn)
    assert msg["type"] == "ERROR"
    assert msg["msg"] == "Player not assigned to this game"
    assert conn.closed is True


def test_first_player_gets_assigned_index():
    repo = DummyRepo()
    server = Server("g1", ["a", "b"], repo)
    conn = DummyConn()

    ok = server.handle_join_message(
        {"player": "a", "game_id": "g1"},
        conn,
        ("127.0.0.1", 1111),
    )

    assert ok is True
    msgs = parse_all_json(conn)

    assert msgs[0]["type"] == "ASSIGN_IDX"
    assert msgs[0]["idx"] == 0
    assert "a" in server.clients
    assert server.game is None
    assert len(msgs) == 1


def test_second_player_starts_game_and_broadcasts_state():
    repo = DummyRepo()
    server = Server("g1", ["a", "b"], repo)
    conn1 = DummyConn()
    conn2 = DummyConn()

    ok1 = server.handle_join_message(
        {"player": "a", "game_id": "g1"},
        conn1,
        ("127.0.0.1", 1111),
    )
    ok2 = server.handle_join_message(
        {"player": "b", "game_id": "g1"},
        conn2,
        ("127.0.0.1", 2222),
    )

    assert ok1 is True
    assert ok2 is True
    assert server.game is not None

    all_msgs_1 = parse_all_json(conn1)
    all_msgs_2 = parse_all_json(conn2)

    assert any(m["type"] == "STATE" for m in all_msgs_1)
    assert any(m["type"] == "STATE" for m in all_msgs_2)

    assert repo.load_game("g1") is not None


def test_duplicate_player_rejected():
    repo = DummyRepo()
    server = Server("g1", ["a", "b"], repo)
    conn1 = DummyConn()
    conn2 = DummyConn()

    assert server.handle_join_message(
        {"player": "a", "game_id": "g1"},
        conn1,
        ("127.0.0.1", 1111),
    ) is True

    ok = server.handle_join_message(
        {"player": "a", "game_id": "g1"},
        conn2,
        ("127.0.0.1", 2222),
    )

    assert ok is False
    msg = parse_last_json(conn2)
    assert msg["type"] == "ERROR"
    assert msg["msg"] == "Player already connected"
    assert conn2.closed is True


def test_reconnecting_player_gets_assigned_idx_and_current_state():
    repo = DummyRepo()
    server = Server("g1", ["a", "b"], repo)
    conn1 = DummyConn()
    conn2 = DummyConn()

    server.handle_join_message({"player": "a", "game_id": "g1"}, conn1, ("127.0.0.1", 1111))
    server.handle_join_message({"player": "b", "game_id": "g1"}, conn2, ("127.0.0.1", 2222))

    file1 = DummyFile()
    server.handle_disconnect(conn1, file1)
    assert "a" not in server.clients

    conn3 = DummyConn()
    ok = server.handle_join_message(
        {"player": "a", "game_id": "g1"},
        conn3,
        ("127.0.0.1", 3333),
    )

    assert ok is True
    msgs = parse_all_json(conn3)

    assert msgs[0]["type"] == "ASSIGN_IDX"
    assert msgs[0]["idx"] == 0
    assert any(m["type"] == "STATE" for m in msgs)


def test_disconnect_removes_client():
    repo = DummyRepo()
    server = Server("g1", ["a", "b"], repo)
    conn = DummyConn()
    file_obj = DummyFile()

    server.handle_join_message({"player": "a", "game_id": "g1"}, conn, ("127.0.0.1", 1111))
    assert "a" in server.clients

    server.handle_disconnect(conn, file_obj)

    assert "a" not in server.clients
    assert conn.closed is True
    assert file_obj.closed is True


def test_saved_state_is_loaded_when_last_player_joins():
    repo = DummyRepo()

    initial_game = Server("g1", ["a", "b"], repo)
    c1 = DummyConn()
    c2 = DummyConn()
    initial_game.handle_join_message({"player": "a", "game_id": "g1"}, c1, ("127.0.0.1", 1111))
    initial_game.handle_join_message({"player": "b", "game_id": "g1"}, c2, ("127.0.0.1", 2222))

    saved_state = repo.load_game("g1")
    assert saved_state is not None

    repo2 = DummyRepo()
    repo2.games["g1"] = saved_state

    server2 = Server("g1", ["a", "b"], repo2)
    conn3 = DummyConn()
    conn4 = DummyConn()

    server2.handle_join_message({"player": "a", "game_id": "g1"}, conn3, ("127.0.0.1", 3333))
    server2.handle_join_message({"player": "b", "game_id": "g1"}, conn4, ("127.0.0.1", 4444))

    assert server2.game is not None
    assert repo2.load_game("g1") is not None