import os,json
from game_logic.state import GameState
from web.backend.database.RedisRepository import RedisRepository
from server.application.commands.game_commands import PlayCardCommand,GiveHintCommand,DiscardCardCommand
from infrastructure.redis_provider import RedisProvider
import asyncio,websockets
HOST = '0.0.0.0'
PORT = int(os.getenv("PORT","12345"))
GAME_ID = os.getenv("GAME_ID", "testgame")
PLAYERS_JSON = os.getenv("PLAYERS_JSON", '["Alice","Bob"]')
ALLOWED_PLAYERS = json.loads(PLAYERS_JSON)
TIMEOUT = 5000

class Server:
    def __init__(self,game_id,allowed_players,game_repository):
        self.game_id = game_id
        self.allowed_players = allowed_players
        self.expected_players = len(allowed_players)
        self.game_repository = game_repository
        self.clients = {}
        self.player_indices = {name: i for i,name in enumerate(allowed_players)}
        self.game = None
        self.commands = {
            "PLAY": PlayCardCommand(),
            "HINT": GiveHintCommand(),
            "DISC": DiscardCardCommand()
        }
        self.lock = asyncio.Lock()
   
    async def broadcast_state(self):
        """Send current game state to all connected clients after saving to game repository."""
        snap = self.game.serialize_state()
        try:
            self.game_repository.save_game(self.game_id, snap) # we should think about making this async so to not block server with slow sync repo write/read
        except Exception as e:
            print(f"[ERROR] Could not persist game state: {e}", flush=True)

        msg = json.dumps({"type": "STATE", **snap})
        dead = []
        for name, ws in self.clients.items():
            try:
                await ws.send(msg)
            except:
                dead.append(name)

        for name in dead:
            del self.clients[name]
        
    async def handle_join_message(self,join,websocket):
        name   = join.get("player")
        game_id = join.get("game_id") 

        async with self.lock: 
            if game_id != self.game_id:
                await websocket.send(json.dumps({"type":"ERROR","msg":"Wrong game_id"}))
                await websocket.close()
                return False

            if name not in self.allowed_players:
                await websocket.send(json.dumps({"type":"ERROR","msg":"Player not assigned to this game"}))
                await websocket.close()
                return False

            if name in self.clients:
                await websocket.send(json.dumps({"type":"ERROR","msg":"Player already connected"}))
                await websocket.close()
                return False

            self.clients[name] = websocket
            idx = self.player_indices[name]
            await websocket.send(json.dumps({"type":"ASSIGN_IDX","idx":idx}))

            if len(self.clients) == self.expected_players and self.game is None:
                saved_state = self.game_repository.load_game(self.game_id)
                if saved_state:
                    self.game = GameState.from_serialized(saved_state)
                else:
                    self.game = GameState(self.allowed_players)
                await self.broadcast_state()
            elif self.game is not None:
                await self.broadcast_state()
        return True
    
    async def handle_action_message(self,msg,websocket):
        async with self.lock: 
                    if not self.game:
                        return
                    try:
                        cmd_type = msg.get("type")
                        command = self.commands.get(cmd_type)
                        if not command:
                            raise ValueError(f"Unknown command type: {cmd_type}")
                        command.execute(self,msg)
                        await self.broadcast_state()
                    except Exception as e:
                        await websocket.send(json.dumps({
                            "type": "ERROR",
                            "msg": str(e)
                        }))
    
    async def handle_disconnect(self,websocket):
        async with self.lock:
            for name, ws in list(self.clients.items()):
                if ws == websocket:
                    del self.clients[name]
                    break

    async def handle_client(self, websocket):
        '''loop that handles client messages depending on whether all have joined.'''
        try:
            '''JOIN STATE'''
            raw = await websocket.recv()
            join = json.loads(raw)
            should_continue = await self.handle_join_message(join,websocket)
            if not should_continue:
                return
            
            async for raw in websocket:
                '''ACTION state'''
                msg = json.loads(raw)
                await self.handle_action_message(msg,websocket)

        except websockets.exceptions.ConnectionClosed:
            pass

        finally:
            '''DISCONNECT STATE'''
            await self.handle_disconnect(websocket)
        
async def main():
    redis_provider = RedisProvider()
    game_repo = RedisRepository(
        redis_provider.get_master_client(),
        redis_provider.get_master_client
    )

    server = Server(GAME_ID, ALLOWED_PLAYERS, game_repo)

    async def handler(websocket):
        await server.handle_client(websocket)

    await websockets.serve(handler, HOST, PORT)

    print(f"WebSocket server running on {HOST}:{PORT}")
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())