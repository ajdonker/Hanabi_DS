import pytest
from server.application.gameServerManager import GameServerManager
# testing integration of matchmaking with GameServerManager container service 

@pytest.fixture(autouse=True)
def cleanup_containers():
    manager = GameServerManager()
    yield
    manager.cleanup_leftover_games()

def test_spawn_container():
    manager = GameServerManager()

    host, port, name = manager.spawn_server_container(
        "test123",
        ["alice", "bob"]
    )

    assert host == "127.0.0.1"
    assert isinstance(port, int)
    assert "hanabi-game-test123" in name

    manager.remove_container(name)

def test_container_lifecycle():
    manager = GameServerManager()

    _, _, name = manager.spawn_server_container(
        "test456",
        ["alice"]
    )

    status = manager.get_container_status(name)
    assert status in ("running", "created")

    removed = manager.remove_container(name)
    assert removed is True

    status_after = manager.get_container_status(name)
    assert status_after is None

def test_cleanup_leftovers():
    manager = GameServerManager()

    names = []
    for i in range(3):
        _, _, name = manager.spawn_server_container(
            f"cleanup{i}",
            ["p1"]
        )
        names.append(name)

    manager.cleanup_leftover_games()

    for name in names:
        status = manager.get_container_status(name)
        assert status is None

def test_spawn_container_port_exposed():
    manager = GameServerManager()

    host, port, name = manager.spawn_server_container(
        "porttest",
        ["alice"]
    )

    assert port > 0

    manager.remove_container(name)


