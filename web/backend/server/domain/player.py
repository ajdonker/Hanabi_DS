from web.backend.server.domain.cards import HandCard
from web.backend.server.domain.cards import Card

class Player():
    def __init__(self, username:str, hand:list[HandCard]):
        self.username = username
        self.hand = hand

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
        self.hand.insert(0, HandCard) 

    #utils
    def getCardByID(self, cardIndex) -> HandCard:
        return self.hand[cardIndex]
        
