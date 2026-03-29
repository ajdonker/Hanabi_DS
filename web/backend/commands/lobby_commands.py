from commands import Command
from database.repos import RedisRepository

class CreateLobbyCommand(Command):
    def __init__(self):
        self.lobbyRepository = RedisRepository()
        self.lobbyInitializer = LobbyInitializer()
        
    def execute(self, data):
        pass
        #here's where we can join our code in your matchmaker class
    
class JoinLobbyCommand(Command):
    def __init__(self):
        self.lobbyRepository = RedisRepository()
        self.gameInitializer = GameInitializer()
    
    def execute(self, data):
        pass 
        #here's where we can join our code in your matchmeker class
    