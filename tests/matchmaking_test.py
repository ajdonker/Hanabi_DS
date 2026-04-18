import pytest
from unittest.mock import MagicMock
from server.application.matchmakingService import MatchmakingService
from server.application.waitingPlayer import WaitingPlayer
import threading, random, time

@pytest.fixture
def matchmaking():
    mock_manager = MagicMock()
    mock_repo = MagicMock()
    mock_manager.spawn_server_container.return_value = (
        "127.0.0.1",
        5555,
        "test-container"
    )

    service = MatchmakingService(repo=mock_repo)
    service.gameServer_manager = mock_manager
    return service


def test_matchmaking_creates_game(matchmaking):
    matchmaking.create_lobby("l1", 2, "alice")

    p1 = WaitingPlayer("1", "alice", "l1")
    p2 = WaitingPlayer("2", "bob", "l1")

    matchmaking.join_lobby("l1", p1)
    result = matchmaking.join_lobby("l1", p2)

    assert result == "MATCH_FOUND"
    assert len(matchmaking.active_games) == 1

    game = list(matchmaking.active_games.values())[0]

    assert game.container_name == "test-container"
    assert [p.name for p in game.players] == ["alice", "bob"]
    assert matchmaking.repo.save_game_information.called


def test_cleanup_removes_dead_game(matchmaking):
    matchmaking.gameServer_manager.get_container_status.return_value = "exited"

    matchmaking.create_lobby("l1", 1, "alice")
    p1 = WaitingPlayer("1", "alice", "l1")
    matchmaking.join_lobby("l1", p1)

    matchmaking.cleanup_games()

    assert len(matchmaking.active_games) == 0

def test_multiple_lobbies_isolated(matchmaking):
    matchmaking.create_lobby("l1", 2, "alice")
    matchmaking.create_lobby("l2", 2, "charlie")

    matchmaking.join_lobby("l1", WaitingPlayer("1", "alice", "l1"))
    matchmaking.join_lobby("l2", WaitingPlayer("2", "charlie", "l2"))

    # add second players
    res1 = matchmaking.join_lobby("l1", WaitingPlayer("3", "bob", "l1"))
    res2 = matchmaking.join_lobby("l2", WaitingPlayer("4", "dave", "l2"))

    assert res1 == "MATCH_FOUND"
    assert res2 == "MATCH_FOUND"
    assert len(matchmaking.active_games) == 2

def test_duplicate_player_not_added_twice(matchmaking):
    matchmaking.create_lobby("l1", 2, "alice")

    p = WaitingPlayer("1", "alice", "l1")

    matchmaking.join_lobby("l1", p)
    matchmaking.join_lobby("l1", p)  

    assert len(matchmaking.waiting_players) == 1

def test_remove_waiting_player(matchmaking):
    matchmaking.create_lobby("l1", 3, "alice")

    matchmaking.join_lobby("l1", WaitingPlayer("1", "alice", "l1"))
    matchmaking.join_lobby("l1", WaitingPlayer("2", "bob", "l1"))

    matchmaking.remove_waiting_player("bob")

    names = [p.name for p in matchmaking.waiting_players]
    assert "bob" not in names

def test_cleanup_removes_dead_game(matchmaking):
    matchmaking.gameServer_manager.get_container_status.return_value = "exited"

    matchmaking.create_lobby("l1", 1, "alice")
    matchmaking.join_lobby("l1", WaitingPlayer("1", "alice", "l1"))

    assert len(matchmaking.active_games) == 1

    matchmaking.cleanup_games()

    assert len(matchmaking.active_games) == 0

def test_find_game_by_player(matchmaking):
    matchmaking.create_lobby("l1", 2, "alice")

    matchmaking.join_lobby("l1", WaitingPlayer("1", "alice", "l1"))
    matchmaking.join_lobby("l1", WaitingPlayer("2", "bob", "l1"))

    game = matchmaking.find_game_by_player("alice")

    assert game is not None
    assert "alice" in [p.name for p in game.players]

def test_concurrent_joins(matchmaking):
    matchmaking.create_lobby("l1", 3, "alice")

    def join(name):
        matchmaking.join_lobby("l1", WaitingPlayer(name, name, "l1"))

    threads = [
        threading.Thread(target=join, args=(name,))
        for name in ["alice", "bob", "charlie"]
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(matchmaking.active_games) == 1

def test_lobby_exact_capacity(matchmaking):
    matchmaking.create_lobby("l1", 2, "alice")

    matchmaking.join_lobby("l1", WaitingPlayer("1", "alice", "l1"))
    result = matchmaking.join_lobby("l1", WaitingPlayer("2", "bob", "l1"))

    assert result == "MATCH_FOUND"
    assert len(matchmaking.waiting_players) == 0

def test_concurrent_overflow_players(matchmaking):
    matchmaking.create_lobby("l1", 2, "alice")

    results = []

    def join(name):
        res = matchmaking.join_lobby("l1", WaitingPlayer(name, name, "l1"))
        results.append(res)

    threads = [
        threading.Thread(target=join, args=(name,))
        for name in ["alice", "bob", "charlie"]
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(matchmaking.active_games) == 1

    total_players_in_games = sum(len(g.players) for g in matchmaking.active_games.values())
    assert total_players_in_games == 2

    assert len(matchmaking.waiting_players) == 1

def test_high_concurrency_with_delays(matchmaking):
    lobby_size = 4
    total_players = 40

    matchmaking.create_lobby("l1", lobby_size, "p0")

    def join(i):
        time.sleep(random.uniform(0, 0.01))  # simulate network jitter
        name = f"p{i}"
        matchmaking.join_lobby("l1", WaitingPlayer(str(i), name, "l1"))

    threads = [
        threading.Thread(target=join, args=(i,))
        for i in range(total_players)
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    expected_games = total_players // lobby_size

    assert len(matchmaking.active_games) == expected_games

    for game in matchmaking.active_games.values():
        assert len(game.players) == lobby_size

def test_no_duplicate_players(matchmaking):
    lobby_size = 3
    total_players = 30

    matchmaking.create_lobby("l1", lobby_size, "p0")

    def join(i):
        name = f"p{i}"
        matchmaking.join_lobby("l1", WaitingPlayer(str(i), name, "l1"))

    threads = [
        threading.Thread(target=join, args=(i,))
        for i in range(total_players)
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    all_players = []

    for game in matchmaking.active_games.values():
        all_players.extend([p.name for p in game.players])

    all_players.extend([p.name for p in matchmaking.waiting_players])

    assert len(all_players) == len(set(all_players))