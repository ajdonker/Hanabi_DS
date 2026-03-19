import redis,os
import socket, threading, json,time
from game_logic.state import GameState
from game_logic.cards import Color
from redis.sentinel import Sentinel

HOST = '0.0.0.0'
PORT = int(os.getenv("PORT","12345"))
# refactored to use sentinel 
# REDIS_HOST = os.getenv("REDIS_HOST", "redis")
# REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

GAME_ID = os.getenv("GAME_ID", "testgame")
PLAYERS_JSON = os.getenv("PLAYERS_JSON", '["Alice","Bob"]')
SENTINEL_NODES  = os.getenv("SENTINEL_NODES", "sentinel:26379").split(",")
SENTINEL_MASTER = os.getenv("SENTINEL_MASTER_NAME", "mymaster")
ALLOWED_PLAYERS = json.loads(PLAYERS_JSON)
TIMEOUT = 5000
# Parse "host:port" list into tuples
sentinel_endpoints = []
for node in SENTINEL_NODES:
    host, port = node.split(":")
    sentinel_endpoints.append((host, int(port)))

# Connect via Sentinel
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


class Server:
    def __init__(self,game_id,allowed_players,redis_client):
        self.game_id = game_id
        self.allowed_players = allowed_players
        self.expected_players = len(allowed_players)
        self.redis = redis_client
        self.clients = {}
        self.player_indices = {name: i for i,name in enumerate(allowed_players)}
        self.game = None
        self.lock = threading.Lock()
    def get_state_with_retry(self, retries=10, delay=0.5):
        key = f"hanabi:state:{self.game_id}"

        for attempt in range(retries):
            try:
                return self.redis.get(key)
            except Exception as e:
                print(f"[WARN] Redis read failed {attempt+1}/{retries}: {e}", flush=True)
                try:
                    self.redis = get_master_client()
                except Exception as inner:
                    print(f"[WARN] Recreating Redis client failed: {inner}", flush=True)
                time.sleep(delay)

        raise RuntimeError(f"Could not read state for {self.game_id}")
    def broadcast_state(self):
        """Send current game state to all connected clients.
        When master changed, rediscover master client"""
        #global r
        snap = self.game.serialize_state()
        snap_json = json.dumps(snap)
        msg  = json.dumps({"type":"STATE", **snap}) + "\n"
        state_key = f"hanabi:state:{self.game_id}"
        # persist for future reloads
        for attempt in range(2):
            try:
                self.redis.set(state_key,snap_json) # to check if race condition possible. shouldnt be because 1 server 
                # can write to only the one game id it is given?
                self.redis.set("hanabi:state", msg.strip())
                break
            except (redis.exceptions.ReadOnlyError, redis.exceptions.ConnectionError) as e:
                # Master has been demoted, re-fetch the new one
                print("[WARN] Master changed, re-discovering via Sentinel:", e)
                
                self.redis = get_master_client()
        else:
            print("[ERROR] Could not write to Redis master after retry")
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
                raw = self.get_state_with_retry()
                if raw:
                    self.game = GameState.from_serialized(json.loads(raw))
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
                line = conn_file.readline()
                if not line:
                    break
                msg = json.loads(line)
                self.handle_action_message(msg,conn)
        finally:
            self.handle_disconnect(conn,conn_file)
        
def main():
    r = get_master_client()
    print(f"[*] Connected to Redis master via Sentinel '{SENTINEL_MASTER}' at {sentinel_endpoints}")
    server = Server(GAME_ID,ALLOWED_PLAYERS,r)
    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            threading.Thread(target=server.handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()