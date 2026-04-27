import asyncio
import json
from database.RedisRepository import RedisRepository
from server.events import Event
from server.presentation.connection_manager import ConnectionManager
class TurnWatcher:
    def __init__(self, repo: RedisRepository, connection_manager : ConnectionManager):
        self.repo = repo
        self.connection_manager = connection_manager
    
    async def start(self):
        #monitors the game timers and force next turn if expired
        while True:
            try:
                games = self.repo.get_all_games()
                
                for game in games:
                    if game.isTurnExpired():
                        game.changeTurn()
                        self.repo.save_game(game)

                        connections = self.connection_manager.get_game_connections(game.gameID)

                        payload = {
                            "type": "event_batch",
                            "events": [ {
                                    "event": "turn_changed",
                                    "data": {"nextPlayer": game.playerTurn}
                                    }]
                        }

                        for ws in connections:
                            await ws.send_text(json.dumps(payload))
                                    
                await asyncio.sleep(1)
            
            except Exception as e:
                print(f"[TurnWatcher] Error: {e}")
                await asyncio.sleep(1)
                
                
