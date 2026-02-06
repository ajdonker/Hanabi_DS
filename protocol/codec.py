# protocol/codec.py
import json

def encode(msg: dict) -> bytes:
    return (json.dumps(msg) + "\n").encode()

def decode(line: str) -> dict:
    return json.loads(line)
