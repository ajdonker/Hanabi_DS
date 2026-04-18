import json

class MockRedisRepository:
    def __init__(self):
        self.users = {} 

    def get(self, key):
        if key.startswith("hanabi:user:"):
            username = key.split(":")[-1]
            user = self.users.get(username)
            return json.dumps(user) if user else None
        return None
    
    def set(self, key, value):
        if key.startswith("hanabi:user:"):
            username = key.split(":")[-1]
            self.users[username] = json.loads(value)