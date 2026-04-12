import json

class MockRedisRepository:
    def __init__(self):
        self.users = {} 
        self.games = {}

    def get(self, key):
        if key.startswith("hanabi:user:"):
            username = key.split(":")[-1]
            user = self.users.get(username)
            return json.dumps(user) if user else None
        elif key.startswith("hanabi:game:"):
            game_id = key.split(":")[-1]
            game = self.games.get(game_id)
            return json.dumps(game) if game else None
        return None
    
    def set(self, key, value):
        if key.startswith("hanabi:user:"):
            username = key.split(":")[-1]
            self.users[username] = json.loads(value)
        elif key.startswith("hanabi:game:"):
            game_id = key.split(":")[-1]
            self.games[game_id] = json.loads(value)