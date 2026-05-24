import base64
import hashlib
import json
import os
import time


class AuthenticationService:
    def __init__(self, secret: str | None = None, duration_seconds: int = 24 * 60 * 60):
        self.secret = secret or os.getenv("AUTH_TOKEN_SECRET")
        self.duration_seconds = duration_seconds

    def generate_token(self, username: str) -> str:
        expires_at = int(time.time() + self.duration_seconds)
        payload = {
            "username": username,
            "expires_at": expires_at,
            "signature": self._signature(username, expires_at),
        }
        encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        return base64.b64encode(encoded).decode("utf-8")

    def validate_token(self, token: str | None) -> str | None:
        try:
            decoded = base64.b64decode(token.encode("utf-8"))
            payload = json.loads(decoded.decode("utf-8"))
        except Exception:
            return None

        username = payload.get("username")
        expires_at = payload.get("expires_at")
        signature = payload.get("signature")

        if expires_at <= int(time.time()):
            return None

        expected = self._signature(username, expires_at)
        if signature != expected:
            return None

        return username

    def _signature(self, username: str, expires_at: int) -> str:
        message = f"{username}{expires_at}{self.secret}"
        return hashlib.sha256(message.encode("utf-8")).hexdigest()
