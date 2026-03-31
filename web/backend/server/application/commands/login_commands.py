from database.repos import IGameRepository, ILobbyRepository, IUserRepository
from commands import Command
from presentation.event import Event
from database.GameRepo import RedisRepository

class RegisterCommand(Command):
    def __init__(self):
        self.userRepository = RedisRepository()
        
    def execute(self, data):
        username = data["username"]
        password = data["password"] #of course you'd want to hash this, it's just a blueprint

        if self.userRepository.get_user(username):
            return [
                Event("error", {"message": "Username already exists"})
            ]

        self.userRepository.save_user(username, password)

        return [
            Event("registration_success", {"message": "Registration successful"})
        ]

class LoginCommand(Command):
    def __init__(self):
        self.userRepository = RedisRepository()
        
    def execute(self, data):
        username = data["username"]
        password = data["password"]

        user = self.userRepository.get_user(username)

        if not user or user.password != password:
            return [
                Event("error", {"message": "Invalid username or password"})
            ]

        return [
            Event("login_success", {"message": "Login successful"})
        ]