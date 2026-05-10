from database.RedisRepository import RedisRepository
from database.mockRedis import MockRedisRepository


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
