class MatchmakingService:

    def __init__(self,repo,lobby_size = 2):
        self.lobby_size = lobby_size
        self.waiting_players = [] 
        self.active_games = {}
        self.active_player_names = {} 

    def create_game(self,players,game_id=None):
        if game_id is None:
            game_id = str(uuid.uuid4())[:8] 
        for p in players:
            self.active_player_names[p.name] = {"status": "active","game_id": game_id}
        player_names = [p.name for p in players]
        host, port, container_name = self.spawn_server_container(game_id,player_names)
        game = GameInformation(
            game_id= game_id,
            container_name = container_name,
            host = host,
            port = port,
            players = players,
            timestamp = time.time()
        )
        self.active_games[game_id] = game
        return game
    

    def add_player_to_pool(self, player: WaitingPlayer) -> MatchResult:
        self.waiting_players.append(player)

        if len(self.waiting_players) < self.lobby_size:
            return MatchResult(status="WAITING")

        players = self.waiting_players[:self.lobby_size]
        self.waiting_players = self.waiting_players[self.lobby_size:]

        game_id = str(uuid.uuid4())[:8]
        player_names = [p.name for p in players]

        server_info = self.game_server_manager.start_game(game_id, player_names)

        game = GameInfo(game_id, player_names)
        self.active_games[game_id] = game

        return MatchResult(
            status="MATCH_FOUND",
            game_info=game
        )
    
    def remove_game(self, game_id):
        with self.lock:
            game = self.active_games.pop(game_id, None)
            if not game:
                return
            try:
                c = self.docker_client.containers.get(game.container_name)
                for p in game.players:
                    self.active_player_names.pop(p.name, None)
                c.stop(timeout=2)
                c.remove()
            except Exception as e:
                print(f"Cleanup failed for {game_id}: {e}")

    def remove_waiting_player(self, conn):
        with self.lock:
            removed_names = [p.name for p in self.waiting_players if p.conn == conn]
            self.waiting_players = [p for p in self.waiting_players if p.conn != conn]
            for name in removed_names:
                self.active_player_names.pop(name, None)


    def find_game(self, game_id, player_name):
        with self.lock:
            game = self.active_games.get(game_id)
            if game is None:
                return None

            player_names = [p.name for p in game.players]
            if player_name not in player_names:
                return None
            return game

    #application layer  
    def find_game_by_player(self, player_name):
        with self.lock:
            for game in self.active_games.values():
                player_names = [p.name for p in game.players]
                print(player_names)
                if player_name in player_names:
                    print(f"Game found for player {player_name}")
                    return game
            print(f"No active game found for player {player_name}")
            return None