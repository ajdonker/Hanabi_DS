from web.backend.server.domain.cards import HandCard


class Player():
    def __init__(self, playerID:str, name:str, hand:list[HandCard]):
        self.playerID = playerID
        self.name = name
        self.hand = [None]*5

    def getHand(self) -> list[HandCard]:
        return self.hand

    def getCard(self, cardIndex):
        self.hand[cardIndex]        

    def addCard(self, card : HandCard): 
        self.hand.append(card)
    
    def removeCard(self, card):
        if card in self.hand:
            self.hand.remove(card)
    
