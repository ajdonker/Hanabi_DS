from database.RedisRepository import RedisRepository, IUserRepository
from server.events import Event
from server.presentation.connection_manager import ConnectionManager
from.handler import IHandler
from server.domain.exceptions import *
from server.domain.exceptionMapper import ExceptionMapper
from server.application.commands.auth_commands import LoginCommand,RegisterCommand
from server.application.user import User
import hashlib

class RegisterHandler(IHandler):
    def __init__(self, repository: IUserRepository = None):
        self.userRepository = repository
        
    def execute(self, command: RegisterCommand):
        user = User(command.full_name, command.username, command.email, command.password)
        
        if self.userRepository.load_user(command.username): #if return something, user already exists
            return [Event("error", {"message": "Username already exists"})]
        
        try :
            self.userRepository.save_user(user)
        except RuntimeError:
            return [Event("error", {"message": "Temporary server issue"})]
        
        return [Event("registration_success", {"message": "Registration successful"})]
    
class LoginHandler(IHandler):
    def __init__(self, repository: RedisRepository = None):
        self.repository = repository
        
    def execute(self, command: LoginCommand):
        username = command.username
        password = command.password
        
        user = self.repository.load_user(username)
        if user is None :
            return [Event("error", {"message": "User not found"})]
        
        if user._hashedPass != hashlib.sha256(password.encode('utf-8')).hexdigest():
            return [Event("error", {"message": "Invalid username or password"})]
           
        game_id = self.repository.get_player_game_mapping(username)

        if game_id: #there's already a valid game for that player
            game_info = self.repository.load_game_information(game_id)
            
            return [Event("player_reconnected", {
                "player_name": username,
                "game_id": game_id,
                "host": game_info.host,
                "port": game_info.port
            })]
            
        else:
            return [Event("login_success", {"message": "Login successful", "player_name": username})]
