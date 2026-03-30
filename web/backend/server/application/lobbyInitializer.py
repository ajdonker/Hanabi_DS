class LobbyInitializer:

    def create_lobby(self, name: str, max_users: int):
        return Lobby(name=name, max_users=max_users)

    def add_player(self, lobby, player):
        if lobby.is_full():
            raise Exception("Lobby is full")
        lobby.add_player(player)