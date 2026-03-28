from redis.sentinel import Sentinel
import os

class RedisProvider:
    def __init__(self):
        sentinel_nodes = os.getenv("SENTINEL_NODES", "sentinel:26379").split(",")
        master_name = os.getenv("SENTINEL_MASTER_NAME", "mymaster")

        endpoints = []
        for node in sentinel_nodes:
            host, port = node.split(":")
            endpoints.append((host, int(port)))

        self.master_name = master_name 
        self.sentinel = Sentinel(endpoints, socket_timeout=1.0)

    def get_master_client(self):
        return self.sentinel.master_for(
            self.master_name,
            socket_timeout=1.0,
            decode_responses=True
        )