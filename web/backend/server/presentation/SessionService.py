from database.RedisRepository import RedisRepository

class SessionService:
    def __init__(self, repo: RedisRepository):
        self.repo = repo

    def get_game_id(self, player_id: str) -> str | None:
        return self.repo.get_player_game_mapping(player_id)