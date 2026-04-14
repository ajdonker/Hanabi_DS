from abc import ABC, abstractmethod
from server.domain.cards import Color,Number

class GameInterface(ABC):

    @property
    @abstractmethod
    def gameID(self):
        pass
    
    @property
    @abstractmethod
    def board(self):
        pass
    
    @property
    @abstractmethod
    def players(self):
        pass
    
    @property
    @abstractmethod
    def turnOrder(self):
        pass
    
    @property
    @abstractmethod
    def playerTurn(self):
        pass

    @property
    @abstractmethod
    def finalTurn(self):
        pass

    @abstractmethod
    def getPlayer(self, username: str):
        pass

    @abstractmethod
    def playCard(self, username: str, cardIndex: int):
        pass

    @abstractmethod
    def giveHint(self, username: str, target: str, *, color: Color = None, number: Number = None):
        pass

    @abstractmethod
    def discardCard(self, username: str, cardIndex: int):
        pass


