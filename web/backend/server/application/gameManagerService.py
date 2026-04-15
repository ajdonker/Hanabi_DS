# infrastructure/game_server_manager.py
import docker
import json
import os
import time

SERVER_TIMEOUT_TIME = 50000

class GameServerManager:

    def __init__(self):
        self.docker_client = docker.from_env()

    #spawn a container then return its information
    def spawn_server_container(self,game_id,player_names):
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