from server.domain.cards import HandCard
from server.domain.cards import Card

class Player():
    def __init__(self, username:str, hand:list[HandCard] = None):
        self._username = username
        self._hand = hand if hand is not None else []
        self._lastTurn = False #used for checking GameOver

    #getters
    @property
    def getHand(self) -> list[HandCard]:
        return self._hand

    @property
    def getUsername(self) -> str:
        return self._username
    
    def setHand(self, hand: list[HandCard]):
        self._hand = hand

    def getLastTurn(self):
        return self._lastTurn
    
    def setLastTurn(self, value: bool):
        self._lastTurn = value
        
    #player actions
    def removeCard(self, cardIndex: int):
        card = self._hand.pop(cardIndex)
        card.removeHints()
        return card

    def addCard(self, card : HandCard):
        if card is not None and not isinstance(card, HandCard):
            raise TypeError("Expected HandCard")
        if(card is None):
            self._lastTurn = True #it's player last turn ??
        else:
            self._hand.insert(0, card) 

    def addCardAt(self, index: int, card: HandCard):
        if card is not None and not isinstance(card, HandCard):
            raise TypeError("Expected HandCard")
        if(card is None):
            self._lastTurn = True #it's player last turn ??
        else:
            self._hand.insert(index, card) 

    #utils
    def getCardByID(self, cardIndex) -> HandCard:
        if cardIndex < 0 or cardIndex >= len(self._hand):
            raise IndexError("Invalid card index")
        return self._hand[cardIndex]
        
