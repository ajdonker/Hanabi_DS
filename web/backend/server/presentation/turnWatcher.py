import asyncio
import json
from database.RedisRepository import RedisRepository
from server.presentation.connection_manager import ConnectionManager


class TurnWatcher:
    def __init__(self, repo: RedisRepository, connection_manager : ConnectionManager, game_id: str):
        self.repo = repo
        self.connection_manager = connection_manager
        self.game_id = game_id

    async def check_turn(self):
        #print(f"[TurnWatcher] Checking turn for game {self.game_id}")
        game = self.repo.load_game(self.game_id)
        if game is None:
            return

        if not game.isTurnExpired():
            return

        game.changeTurn()
        self.repo.save_game(game)

        connections = self.connection_manager.get_game_connections(game.gameID)

        payload = {
            "type": "event_batch",
            "events": [{
                "event": "turn_change",
                "data": {"next_player": game.playerTurn}
            }]
        }

        for ws in connections:
            await ws.send_text(json.dumps(payload))
    
    async def start(self):
        #monitors the game timers and force next turn if expired
        while True:
            try:
                await self.check_turn()
                await asyncio.sleep(1)
            
            except Exception as e:
                print(f"[TurnWatcher] Error: {e}")
                await asyncio.sleep(1)
                
                
