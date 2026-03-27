from web.backend.server.domain.cards import HandCard
from web.backend.server.domain.cards import Card

class Player():
    def __init__(self, username:str, hand:list[HandCard]):
        self.username = username
        self.hand = hand
        self.lastTurn = False #used for checking GameOver

    #getters
    @property
    def getHand(self) -> list[HandCard]:
        return self.hand

    @property
    def getUsername(self) -> str:
        return self.username
    
    #player actions
    def removeCard(self, cardIndex : int):
        self.hand.pop(cardIndex)

    def addCard(self, card : HandCard):
        
        if(card is None):
            self.lastTurn = True #it's player last turn
        else:
            self.hand.insert(0, HandCard) 

    #utils
    def getCardByID(self, cardIndex) -> HandCard:
        return self.hand[cardIndex]
        
