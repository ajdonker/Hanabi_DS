class Lobby:
    def __init__(self, name: str, max_users: int):
        self.name = name
        self.max_users = max_users
        self.players = []

    def is_full(self):
        return len(self.players) >= self.max_users

    def add_player(self, player):
        if not self.is_full():
            self.players.append(player)
        else:
            raise Exception("Cannot add player, lobby is full")


class LobbyInitializer:

    def create_lobby(self, name: str, max_users: int):
        return Lobby(name=name, max_users=max_users)

    def add_player(self, lobby, player):
        if lobby.is_full():
            raise Exception("Lobby is full")
    
        lobby.add_player(player)