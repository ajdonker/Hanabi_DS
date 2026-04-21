import asyncio
from database.RedisRepository import RedisRepository

class TurnWatcher:
    def __init__(self, repo: RedisRepository):
        self.repo = repo
    
    async def start(self):
        #monitors the game timers and force next turn if expired
        while True:
            try:
                games = self.repo.get_all_games()
                
                for game in games:
                    if game.isTurnExpired():
                        game.changeTurn()
                        #return event 
                
                await asyncio.sleep(1)
            except Exception as e:
                print(f"[TurnWatcher] Error: {e}")
                await asyncio.sleep(1)
                
                