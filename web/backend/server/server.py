import os,socket, threading, json
from game_logic.state import GameState
from database.GameRepo import RedisRepository
from commands.commands import PlayCardCommand,GiveHintCommand,DiscardCardCommand
from web.backend.server.infrastructure.redis_provider import RedisProvider

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
        self.lock = threading.Lock()
   
    def broadcast_state(self):
        """Send current game state to all connected clients after saving to game repository."""
        #global r
        snap = self.game.serialize_state()
        try:
            self.game_repository.save_game(self.game_id, snap)
        except Exception as e:
            print(f"[ERROR] Could not persist game state: {e}", flush=True)

        msg = json.dumps({"type": "STATE", **snap}) + "\n"
        for conn, addr in self.clients.values():
            try:
                conn.sendall(msg.encode())
            except Exception:
                pass
        
    def handle_join_message(self,join,conn,addr):
        name   = join.get("player")
        game_id = join.get("game_id") 

        with self.lock:
            if game_id != self.game_id:
                conn.sendall((json.dumps({"type":"ERROR","msg":"Wrong game_id"}) + "\n").encode())
                conn.close()
                return False

            if name not in self.allowed_players:
                conn.sendall((json.dumps({"type":"ERROR","msg":"Player not assigned to this game"}) + "\n").encode())
                conn.close()
                return False

            if name in self.clients:
                conn.sendall((json.dumps({"type":"ERROR","msg":"Player already connected"}) + "\n").encode())
                conn.close()
                return False

            self.clients[name] = (conn, addr)
            idx = self.player_indices[name]
            conn.sendall((json.dumps({"type":"ASSIGN_IDX","idx":idx}) + "\n").encode())

            if len(self.clients) == self.expected_players and self.game is None:
                saved_state = self.game_repository.load_game(self.game_id)
                if saved_state:
                    self.game = GameState.from_serialized(saved_state)
                else:
                    self.game = GameState(self.allowed_players)
                self.broadcast_state()
            elif self.game is not None:
                snap = self.game.serialize_state()
                self.broadcast_state()
        return True
    
    def handle_action_message(self,msg,conn):
        if not self.game:
            return 
        with self.lock:
                    try:
                        cmd_type = msg.get("type")
                        command = self.commands.get(cmd_type)
                        if not command:
                            raise ValueError(f"Unknown command type: {cmd_type}")
                        command.execute(self,msg)
                        self.broadcast_state()
                    except Exception as e:
                        err = json.dumps({"type":"ERROR","msg":str(e)}) + "\n"
                        conn.sendall(err.encode())
    
    def handle_disconnect(self,conn,conn_file):
        with self.lock:
            for player_name, (player_conn, _) in list(self.clients.items()):
                if player_conn == conn:
                    del self.clients[player_name]
                    break

            conn_file.close()
            conn.close()

    def handle_client(self, conn, addr):
        '''loop that handles client messages depending on whether all have joined.'''
        conn_file = conn.makefile('r')
        try:
            '''JOIN STATE'''
            line = conn_file.readline()
            if not line:
                conn.close()
                return
            join = json.loads(line)
            should_continue = self.handle_join_message(join,conn,addr)
            if not should_continue:
                conn.close()
                return
            while True:
                '''ACTION state'''
                line = conn_file.readline()
                if not line:
                    break
                msg = json.loads(line)
                self.handle_action_message(msg,conn)
        finally:
            '''DISCONNECT STATE'''
            self.handle_disconnect(conn,conn_file)
        
def run_server_socket(server, host, port):
    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()
        while True:
            conn, addr = s.accept()
            threading.Thread(target=server.handle_client, args=(conn, addr), daemon=True).start()

def main():
    redis_provider = RedisProvider()
    game_repo = RedisRepository(redis_provider.get_master_client(), redis_provider.get_master_client)
    server = Server(GAME_ID,ALLOWED_PLAYERS,game_repo)
    run_server_socket(server,HOST,PORT)

if __name__ == "__main__":
    main()