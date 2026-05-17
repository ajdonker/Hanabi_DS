# infrastructure/game_server_manager.py
import docker, json, os, time

class GameServerManager:

    def __init__(self):
        self.docker_client = None

    def _client(self):
        if self.docker_client is None:
            self.docker_client = docker.from_env()
        return self.docker_client

    def spawn_server_container(self, game_id, player_names):
        """Spawn a game server container and return host, port, container_name."""
        container_name = f"hanabi-game-{game_id}"
        container_port = "8000"

        container = self._client().containers.run(
            image="hanabi-server",
            detach=True,
            name=container_name,
            command=[
                "python",
                "-m",
                "uvicorn",
                "server.main:app",
                "--host",
                "0.0.0.0",
                "--port",
                container_port,
            ],
            environment={
                "GAME_ID": game_id,
                "PLAYERS_JSON": json.dumps(player_names),
                "PORT": container_port,
                "IS_GAME_SERVER": "1",
                "SENTINEL_NODES": os.getenv("SENTINEL_NODES", "sentinel:26379"),
                "SENTINEL_MASTER_NAME": os.getenv("SENTINEL_MASTER_NAME", "mymaster"),
                "MATCHMAKER_CALLBACK_URL": os.getenv("MATCHMAKER_CALLBACK_URL", "http://hanabi-server:8000"),
                "PYTHONUNBUFFERED": "1",
            },
            ports={f"{container_port}/tcp": None},
            network=os.getenv("DOCKER_NETWORK", "backend_hanabi_net"),
            restart_policy={"Name": "unless-stopped"},
        )

        time.sleep(1)
        container.reload()

        port_info = container.attrs["NetworkSettings"]["Ports"][f"{container_port}/tcp"]
        if not port_info:
            print("[MATCHMAKER] full attrs ports:", port_info)
            try:
                print("[MATCHMAKER] container logs:")
                print(container.logs().decode())
            except Exception as e:
                print("[MATCHMAKER] could not read logs:", e)
            raise RuntimeError(f"Container started but port {container_port}/tcp was not published")

        host = port_info[0]["HostIp"]
        if host == "0.0.0.0":
            host = "127.0.0.1"

        port = int(port_info[0]["HostPort"])
        return host, port, container_name

    def get_container_host_port(self, container_name, container_port="8000"):
        """Return the published host and port for a running game container."""
        try:
            container = self._client().containers.get(container_name)
            container.reload()
            port_info = container.attrs["NetworkSettings"]["Ports"].get(f"{container_port}/tcp")
            if not port_info:
                return None

            host = port_info[0]["HostIp"]
            if host == "0.0.0.0":
                host = "127.0.0.1"

            return host, int(port_info[0]["HostPort"])
        except Exception as e:
            print(f"[MATCHMAKER] Failed reading port for {container_name}: {e}")
            return None

    def ensure_server_container(self, game_id, player_names, container_name=None):
        """Return a running game server, replacing the container if it died."""
        expected_name = container_name or f"hanabi-game-{game_id}"
        status = self.get_container_status(expected_name)

        if status == "running":
            host_port = self.get_container_host_port(expected_name)
            if host_port:
                host, port = host_port
                return host, port, expected_name

            print(f"[MATCHMAKER] Running container {expected_name} has no published port; replacing it")
            self.remove_container(expected_name)
            return self.spawn_server_container(game_id, player_names)

        if status is not None:
            print(f"[MATCHMAKER] Replacing {expected_name}; status is {status}")
            self.remove_container(expected_name)

        return self.spawn_server_container(game_id, player_names)

    def get_container_status(self, container_name):
        """Return Docker container status, or None if container does not exist."""
        try:
            container = self._client().containers.get(container_name)
            container.reload()
            return container.status
        except Exception:
            return None

    def remove_container(self, container_name):
        """Stop and remove a container if it exists."""
        try:
            container = self._client().containers.get(container_name)
            container.reload()
            if container.status == "running":
                container.stop(timeout=2)
            container.remove(force=True)
            return True
        except Exception as e:
            print(f"[MATCHMAKER] Failed removing container {container_name}: {e}")
            return False

    def cleanup_leftover_games(self):
        """Remove all old hanabi game containers."""
        try:
            containers = self._client().containers.list(
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
