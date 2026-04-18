class DummyRepo:
    def __init__(self):
        self.games = {}

    def load_game(self, game_id):
        return self.games.get(game_id)

    def save_game(self, game_id, state_dict):
        self.games[game_id] = state_dict



class DummyDB:
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value):
        self.store[key] = value


class DummyConn:
    def __init__(self):
        self.sent = []
        self.closed = False

    def sendall(self, data: bytes):
        self.sent.append(data.decode())

    def close(self):
        self.closed = True


class DummyFile:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True



