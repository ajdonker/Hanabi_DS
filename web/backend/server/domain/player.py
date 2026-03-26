from web.backend.server.domain.cards import HandCard
from web.backend.server.domain.cards import Card

class Player():
    def __init__(self, username:str, name:str, hand:list[HandCard]):
        self.username = username
        self.name = name
        self.hand = hand

    def getHand(self) -> list[HandCard]:
        return self.hand

    def getCard(self, cardIndex) -> Card:
        return self.hand[cardIndex].card()
        
    def addCard(self, card : HandCard): 
        self.hand.append(card)
    
    def removeCard(self, card):
        if card in self.hand:
            self.hand.remove(card)
    
