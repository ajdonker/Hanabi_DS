import hashlib

from database.repos import IGameRepository, ILobbyRepository, IUserRepository
from server.application.commands.commands import Command
from presentation.event import Event
from database.GameRepo import RedisRepository
from web.backend.server.application.user import User

class RegisterCommand(Command):
    def __init__(self):
        self.userRepository = RedisRepository()
        
    def execute(self, data):
        
        fullName = data["fullName"]
        email = data["email"]
        username = data["username"]
        password = data["password"]

        user = User(fullName, username, email, password)
        
        if self.userRepository.load_user(username): #if return something, user already exists
            return [Event("error", {"message": "Username already exists"})]
        
        try :
            self.userRepository.save_user(user)
        except RuntimeError:
            return [Event("error", {"message": "Temporary server issue"})]
        
        return [Event("registration_success", {"message": "Registration successful"})]

class LoginCommand(Command):
    def __init__(self):
        self.userRepository = RedisRepository()
        
    def execute(self, data):
        
        username = data["username"]
        password = data["password"]

        user = self.userRepository.load_user(username)
        if user is None :
            return [Event("error", {"message": "User not found"})]
        
        if user._hashedPass != hashlib.sha256(password.encode('utf-8')).hexdigest():
            return [Event("error", {"message": "Invalid username or password"})]
        
        return [Event("login_success", {"message": "Login successful"})]