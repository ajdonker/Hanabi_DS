import socket,json,threading,uuid,docker,os,time
from database.GameRepo import RedisGameRepository
from infrastructure.redis_provider import RedisProvider
import redis
HOST = "0.0.0.0"
PORT = 9000
LOBBY_SIZE = 2
QUEUE_SIZE = 5 # refuse conns after this many in q 
MAX_LOAD = 5 # max no of servers connected at the same time
SERVER_TIMEOUT_TIME = 3600 # after this time server container automatically cleaned up 
SENTINEL_NODES  = os.getenv("SENTINEL_NODES", "sentinel:26379").split(",")
SENTINEL_MASTER = os.getenv("SENTINEL_MASTER_NAME", "mymaster")

class WaitingPlayer: # contains only the data needed to keep in check waiting players in q 
    def __init__(self, player_id, name, conn):
        self.player_id = player_id
        self.name = name
        self.conn = conn

class GameInformation: # to keep active games, manage their state ON/OFF
    def __init__(self, game_id, container_name, host, port, players,timestamp):
        self.game_id = game_id #reference to Game class in domain ??
        self.container_name = container_name
        self.host = host
        self.port = port
        self.players = players   # list of str
        self.status = "running"
        self.timestamp = timestamp

class Matchmaker:
    def __init__(self,repo,lobby_size = 2):
        self.lobby_size = lobby_size
        self.waiting_players = [] 
        self.active_games = {}
        self.active_player_names = {} 
        self.lock = threading.Lock()
        self.docker_client = docker.from_env()
        # def make_redis():
        #     return redis.Redis(
        #         host=os.getenv("REDIS_HOST", "redis-master"),
        #         port=int(os.getenv("REDIS_PORT", "6379")),
        #         decode_responses=True
        #     )
        # self.redis_factory = make_redis
        #self.redis = self.redis_factory()
        self.repo = repo


   #matchmakerService --> application
    def add_player_to_pool(self, player):
        with self.lock:
            print(f"[MATCHMAKER] before append: {len(self.waiting_players)} waiting")
            if len(self.waiting_players) >= QUEUE_SIZE:
                return "QUEUE_FULL"
            if player.name in self.active_player_names:
                return "NAME_TAKEN"
            self.waiting_players.append(player)
            self.active_player_names[player.name] = {"status": "waiting","game_id":None}
            print(f"[MATCHMAKER] {player.name} joined queue ({len(self.waiting_players)}/{self.lobby_size})")
            if len(self.waiting_players) >= self.lobby_size:
                players = self.waiting_players[:self.lobby_size]
                print(f"[MATCHMAKER] enough players, creating game for {[p.name for p in players]}")
                self.waiting_players = self.waiting_players[self.lobby_size:]
                game = self.create_game(players)
                print(f"[MATCHMAKER] created game {game.game_id}, notifying players")
                self.notify_players(game)
                return game
            print("[MATCHMAKER] not enough players yet")
            return None
    
    #infrastructure --> GameManagerService 
    def spawn_server_container(self,game_id,player_names):
        #spawn a container then return its information
        container_name = f"hanabi-game-{game_id}"
        container = self.docker_client.containers.run(
            image="hanabi-server", 
            detach=True,
            name=container_name,
            environment={
                "GAME_ID": game_id,
                "PLAYERS_JSON": json.dumps(player_names),
                "PORT": "12345",
                "SENTINEL_NODES": os.getenv("SENTINEL_NODES", "sentinel:26379"),
                "SENTINEL_MASTER_NAME": os.getenv("SENTINEL_MASTER_NAME", "mymaster"),
            },
            ports={"12345/tcp": None},      # publish to a random free host port
            network=os.getenv("DOCKER_NETWORK", "backend_hanabi_net"),
            restart_policy={"Name": "unless-stopped"},
        )
        time.sleep(1)
        container.reload()
        for p in player_names:
            self.repo.save_player_game_mapping(p, game_id)

        self.repo.save_game_players(game_id, player_names)
        port_info = container.attrs["NetworkSettings"]["Ports"]["12345/tcp"]
        if not port_info:
            print("[MATCHMAKER] full attrs ports:", port_info)
            try:
                print("[MATCHMAKER] container logs:")
                print(container.logs().decode())
            except Exception as e:
                print("[MATCHMAKER] could not read logs:", e)
            raise RuntimeError("Container started but port 12345/tcp was not published")
        host = port_info[0]["HostIp"]
        if host == "0.0.0.0":
            host = "127.0.0.1"

        port = int(port_info[0]["HostPort"])
        return host, port, container_name
    
    #matchmakerService --> application
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
    
    #presentation layer
    def notify_players(self,game):
        for idx,player in enumerate(game.players):
            msg = {
                "type": "MATCH_FOUND",
                "game_id": game.game_id,
                "host": game.host,
                "port": game.port,
                "player_idx": idx
            }
            print(f"[MATCHMAKER] sending MATCH_FOUND to {player.name}: {msg}")
            try:
                player.conn.sendall((json.dumps(msg) + "\n").encode())
                print(f"[MATCHMAKER] sent to {player.name}")
            except Exception as e:
                print(f"[MATCHMAKER] failed to send to {player.name}:{e}")

    #applicationLayer
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

    #applicationLayer
    def remove_waiting_player(self, conn):
        with self.lock:
            removed_names = [p.name for p in self.waiting_players if p.conn == conn]
            self.waiting_players = [p for p in self.waiting_players if p.conn != conn]
            for name in removed_names:
                self.active_player_names.pop(name, None)
    
    ##infrastructure
    def cleanup(self):
        with self.lock:
            to_remove = []
            now = time.time()
            for game_id, game in self.active_games.items():
                try:
                    c = self.docker_client.containers.get(game.container_name)
                    c.reload()
                    too_old = (now - game.timestamp) > SERVER_TIMEOUT_TIME
                    dead = c.status in ("exited", "dead")
                    if too_old or dead:
                        to_remove.append(game_id)
                except Exception:
                    to_remove.append(game_id)

        for game_id in to_remove:
            print(f"[MATCHMAKER] Cleaning up expired/dead game {game_id}")
            self.remove_game(game_id)    
    #application layer
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

    #infrastructure
    def cleanup_leftover_games(self):
        try:
            containers = self.docker_client.containers.list(
                all=True,
                filters={"name": "hanabi-game-"}
            )

            for c in containers:
                try:
                    print(f"[MATCHMAKER] Removing container {c.name}")
                    c.remove(force=True)
                except Exception as e:
                    print(f"[MATCHMAKER] Failed removing {c.name}: {e}")
        except Exception as e:
            print(f"[MATCHMAKER] Global cleanup failed: {e}")


def handle_client(conn, addr, matchmaker):
    print(f"[MATCHMAKER] Connection from {addr}")
    conn_file = conn.makefile("r")
    try:
        line = conn_file.readline()
        if not line:
            conn.close()
            return

        msg = json.loads(line)
        msg_type = msg.get("type")
        if msg_type != "JOIN_QUEUE" and msg_type != "RESUME_GAME":
            err = {"type": "ERROR", "msg": "Expected JOIN_QUEUE or RESUME_GAME"}
            conn.sendall((json.dumps(err) + "\n").encode())
            conn.close()
            return
        name = msg.get("player")
        if not name:
            err = {"type": "ERROR", "msg": "Missing player name"}
            conn.sendall((json.dumps(err) + "\n").encode())
            conn.close()
            return
        if msg_type == "RESUME_GAME":
            game_id = matchmaker.repo.get_game_id_for_player(name)
            if not game_id:
                err = {"type": "ERROR", "msg": "No saved game found"}
                conn.sendall((json.dumps(err) + "\n").encode())
                conn.close()
                return

            state = matchmaker.repo.load_game(game_id)
            if not state:
                err = {"type": "ERROR", "msg": "Saved state missing"}
                conn.sendall((json.dumps(err) + "\n").encode())
                conn.close()
                return

            game = matchmaker.active_games.get(game_id)
            if game is None:
                players = matchmaker.repo.get_game_players(game_id)
                wrapped_players = [WaitingPlayer(str(uuid.uuid4())[:8], name, None) for name in players]
                game = matchmaker.create_game(wrapped_players,game_id)

            reply = {
                "type": "MATCH_FOUND",
                "game_id": game.game_id,
                "host": game.host,
                "port": game.port
            }
            conn.sendall((json.dumps(reply) + "\n").encode())
            conn.close()
            return
        else: #JOIN_QUEUE
            player_id = str(uuid.uuid4())[:8]
            player = WaitingPlayer(player_id, name, conn)
            game = matchmaker.add_player_to_pool(player)
            if game == "QUEUE_FULL":
                err = {"type": "ERROR", "msg": "Queue is full, try again later"}
                conn.sendall((json.dumps(err) + "\n").encode())
                conn.close()
                return 
            if game is None:
                waiting_msg = {"type": "WAITING", "msg": "Waiting for more players..."}
                conn.sendall((json.dumps(waiting_msg) + "\n").encode())
            # Keep connection open while player waits / until notified
            while True:
                line = conn_file.readline()
                if not line:
                    break

    except Exception as e:
        print(f"[MATCHMAKER] Error with {addr}: {e}")
    finally:
        matchmaker.remove_waiting_player(conn)
        try:
            conn_file.close()
        except:
            pass
        try:
            conn.close()
        except:
            pass
        print(f"[MATCHMAKER] Closed connection {addr}")

def cleanup_loop(matchmaker):
    while True:
        try:
            matchmaker.cleanup()
        except Exception as e:
            print(f"[MATCHMAKER] cleanup loop error: {e}")
        time.sleep(5)   

def run_matchmaker_socket(matchmaker,host,port):
    try:
        with socket.socket() as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            s.listen()
            print(f"[MATCHMAKER] Listening on {host}:{port}")

            while True:
                conn, addr = s.accept()
                threading.Thread(
                    target=handle_client,
                    args=(conn, addr, matchmaker),
                    daemon=True
                ).start()
    except KeyboardInterrupt:
        print(f"[MATCHMAKER] shutting down..")
    finally:
        matchmaker.cleanup_leftover_games() 
def main():
    redis_provider = RedisProvider()
    repo = RedisGameRepository(redis_provider.get_master_client(),redis_provider.get_master_client)
    matchmaker = Matchmaker(repo=repo,lobby_size=LOBBY_SIZE)
    matchmaker.cleanup_leftover_games()
    threading.Thread(
                target=cleanup_loop,
                args=(matchmaker,),
                daemon=True
            ).start()
    run_matchmaker_socket(matchmaker,HOST,PORT)

if __name__ == "__main__":
    main()