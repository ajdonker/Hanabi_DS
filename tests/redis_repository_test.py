import json

from database.RedisRepository import RedisRepository
from database.mockRedis import MockRedisRepository
from server.application.gameInformation import GameInformation


def test_delete_player_game_mappings_removes_only_player_game_keys():
    redis = MockRedisRepository()
    redis.set("hanabi:player_game:alice", '{"game_id": "g1"}')
    redis.set("hanabi:player_game:bob", '{"game_id": "g2"}')
    redis.set("hanabi:user:alice", '{"username": "alice"}')
    repo = RedisRepository(redis_client=redis)

    repo.delete_player_game_mappings()

    assert redis.deleted == [
        "hanabi:player_game:alice",
        "hanabi:player_game:bob",
    ]
    assert redis.get("hanabi:player_game:alice") is None
    assert redis.get("hanabi:player_game:bob") is None
    assert redis.get("hanabi:user:alice") == '{"username": "alice"}'


def test_save_game_information_accepts_player_name_strings():
    redis = MockRedisRepository()
    repo = RedisRepository(redis_client=redis)
    game_info = GameInformation(
        game_id="g1",
        container_name="hanabi-game-g1",
        players=["alice", "bob"],
        timestamp=123,
        host="127.0.0.1",
        port=5555,
    )

    repo.save_game_information(game_info)

    payload = json.loads(redis.get("hanabi:game_info:g1"))
    assert payload["players"] == ["alice", "bob"]
