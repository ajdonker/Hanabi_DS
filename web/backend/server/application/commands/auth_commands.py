
from database.RedisRepository import RedisRepository
from server.application.user import User

class RegisterCommand():
    def __init__(self, full_name: str, email: str, username: str, password: str):
        self.full_name = full_name
        self.email = email
        self.username = username
        self.password = password


class LoginCommand():
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password