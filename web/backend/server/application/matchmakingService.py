class MatchmakingService:

    def __init__(self, game_server_manager):
        self.game_server_manager = game_server_manager

    def create_game_from_lobby(self, lobby):

        players = lobby.players

        game = self.game_initializer.create_game(players)

        game_id = game.id

        server_info = self.game_server_manager.start_game(
            game_id,
            [p.name for p in players]
        )

        #todo