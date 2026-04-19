from typing import List
from server.application.user import User

class Lobby:
    def __init__(self, name: str, maxUsers: int, numUsers: int, currentUsers:  List[User] | None):
        self.name = name 
        self.maxUsers = maxUsers
        self.numUsers = numUsers 
        self.currentUsers = currentUsers

    def isFull(self):
        return self.numUsers == self.maxUsers