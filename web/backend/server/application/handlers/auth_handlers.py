from database.repos import IUserRepository
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
    def __init__(self, userRepository: IUserRepository, connectionManager : ConnectionManager):
        self.userRepository = userRepository
        self.connectionManager = connectionManager
        
    def execute(self, command: LoginCommand):

        username = command.username
        password = command.password
        
        user = self.userRepository.load_user(username)
        if user is None :
            return [Event("error", {"message": "User not found"})]
        
        if user._hashedPass != hashlib.sha256(password.encode('utf-8')).hexdigest():
            return [Event("error", {"message": "Invalid username or password"})]
           
        game_id = self.userRepository.get_player_game_mapping(username)

        if game_id:
            # reconnect
            connectionManager.join_game(player_id, game_id)
            return [Event("player_reconnected", {...})]
        else:
            return [Event("player_logged", {})]

