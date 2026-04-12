import json
from database.RedisRepository import RedisRepository
from database.mockRedis import MockRedisRepository
from server.application.commands.game_commands import PlayCardCommand


def test_play_card_success_returns_card_correct_and_turn_change():
    mockDB = MockRedisRepository()
    repo = RedisRepository(redis_client=mockDB)
    command = PlayCardCommand(repo)

    mockDB.set(
        "hanabi:game:g1",
        json.dumps(
            {
                "game_id": "g1",
                "player_turn": "P1",
                "final_turn": False,
                "players": [
                    {
                        "username": "P1",
                        "hand": [
                            {"number": "ONE", "color": "RED", "hints": {"color": None, "number": None}},
                            {"number": "FIVE", "color": "BLUE", "hints": {"color": None, "number": None}},
                            {"number": "TWO", "color": "BLUE", "hints": {"color": None, "number": None}},
                            {"number": "ONE", "color": "BLUE", "hints": {"color": None, "number": None}},
                            {"number": "FOUR", "color": "BLUE", "hints": {"color": None, "number": None}},
                        ],
                        "last_turn": False,
                    },
                    {
                        "username": "P2",
                        "hand": [
                            {"number": "THREE", "color": "RED", "hints": {"color": None, "number": None}},
                            {"number": "ONE", "color": "RED", "hints": {"color": None, "number": None}},
                            {"number": "TWO", "color": "BLUE", "hints": {"color": None, "number": None}},
                            {"number": "FOUR", "color": "GREEN", "hints": {"color": None, "number": None}},
                            {"number": "FOUR", "color": "YELLOW", "hints": {"color": None, "number": None}},
                        ],
                        "last_turn": False,
                    },
                ],
                "board": {
                    "piles": {"RED": 0, "YELLOW": 0, "GREEN": 0, "BLUE": 0, "WHITE": 0},
                    "deck_count": 40,
                    "discards": [],
                    "tokens": 8,
                    "misfires": 3,
                },
            }
        ),
    )

    events = command.execute({"gameId": "g1", "playerId": "P1", "cardIndex": 0})

    assert [event.event for event in events] == ["card_correct", "turn_change"]
    assert events[0].data == {"playerId": "P1", "cardIndex": 0}
    assert events[1].data == {"next_player": "P2"}
