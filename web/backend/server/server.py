import redis,os
import socket, threading, json,time
from game_logic.state import GameState
from game_logic.cards import Color
from redis.sentinel import Sentinel
from database.GameRepo import GameRepository
HOST = '0.0.0.0'
PORT = int(os.getenv("PORT","12345"))
GAME_ID = os.getenv("GAME_ID", "testgame")
PLAYERS_JSON = os.getenv("PLAYERS_JSON", '["Alice","Bob"]')
SENTINEL_NODES  = os.getenv("SENTINEL_NODES", "sentinel:26379").split(",")
SENTINEL_MASTER = os.getenv("SENTINEL_MASTER_NAME", "mymaster")
ALLOWED_PLAYERS = json.loads(PLAYERS_JSON)
TIMEOUT = 5000

class Server:
    def __init__(self,game_id,allowed_players,game_repository):
        self.game_id = game_id
        self.allowed_players = allowed_players
        self.expected_players = len(allowed_players)
        #self.redis = redis_client
        self.game_repository = game_repository
        self.clients = {}
        self.player_indices = {name: i for i,name in enumerate(allowed_players)}
        self.game = None
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

        if self.game is not None:
            snap = self.game.serialize_state()
            msg = json.dumps({"type": "STATE", **snap}) + "\n"
            conn.sendall(msg.encode())

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
                conn.sendall((json.dumps({"type":"STATE", **snap}) + "\n").encode())
        return True
    
    def handle_action_message(self,msg,conn):
        if not self.game:
            return 
        with self.lock:
                    try:
                        if msg.get("type") == "PLAY":
                            self.game.play_card(msg["player_idx"], msg["card_idx"])
                        elif msg.get("type") == "HINT":
                            if "color" in msg:
                                self.game.give_hint(msg["from"], msg["to"],color=Color[msg["color"]])
                            elif "number" in msg:
                                self.game.give_hint(msg["from"], msg["to"],number=msg["number"])
                        elif msg.get("type") == "DISC":
                            self.game.discard(msg["player_idx"], msg["card_idx"])
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
        
def main():
    # Parse "host:port" list into tuples
    sentinel_endpoints = []
    for node in SENTINEL_NODES:
        host, port = node.split(":")
        sentinel_endpoints.append((host, int(port)))
    sent = Sentinel(sentinel_endpoints, socket_timeout=1.0)
    def get_master_client():
        """
        Return a fresh Redis client pointing to the current master.
        """
        return sent.master_for(
            SENTINEL_MASTER,
            socket_timeout=1.0,
            decode_responses=True
        )
    r = get_master_client()
    print(f"[*] Connected to Redis master via Sentinel '{SENTINEL_MASTER}' at {sentinel_endpoints}")
    game_repo = GameRepository(r, get_master_client)
    server = Server(GAME_ID,ALLOWED_PLAYERS,game_repo)
    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            threading.Thread(target=server.handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()