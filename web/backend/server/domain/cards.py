import random
from enum import Enum
# 3 card with value 1 for each color
# 2 card with value 2 for each color
# 2 card with value 3 for each color
# 2 card with value 4 for each color
# 1 card with value 5 for each color

class Color(Enum):
    RED, YELLOW, GREEN, BLUE, WHITE = range(5)

class Number(Enum):
    ONE, TWO, THREE, FOUR, FIVE = range(1,6)

class Card():
    def __init__(self, number:Number, color:Color):
        self._number = number
        self._color = color
    
    #getters
    @property 
    def number(self):
        return self._number
    
    @property 
    def color(self):
        return self._color

class HandCard():
    def __init__(self, card:Card):
        self._card = card
        self._hintColor = None
        self._hintNumber = None
    
    @property
    def card(self):
        return self._card
    
    @property
    def color(self):
        return self._card.color

    @property
    def number(self):
        return self._card.number
    
    def setHintColor(self, color:Color):
        self._hintColor = color

    def setHintNumber(self, number:Number):
        self._hintNumber = number

    def removeHints(self):
        self._hintColor = None
        self._hintNumber = None

    def setHints(self, hints: dict):
        if hints is None:
            return
        if hints.get("color"):
            self._hintColor = Color[hints["color"]]
        if hints.get("number"):
            self._hintNumber = Number(hints["number"])
            
    def getHints(self):
        return {
            "color": self._hintColor if self._hintColor else None,
            "number": self._hintNumber if self._hintNumber else None
        }

class Deck():
    def __init__(self):
        self._cards = []
        for color in Color:
            self._cards += [Card(Number.ONE, color)] * 3
            self._cards += [Card(Number.TWO, color)] * 2
            self._cards += [Card(Number.THREE, color)] * 2
            self._cards += [Card(Number.FOUR, color)] * 2
            self._cards += [Card(Number.FIVE, color)] * 1
        self._deck_count = 50

    @staticmethod
    def from_count(count: int):
        deck = Deck()
        deck._cards = [None] * count
        deck._deck_count = count
        return deck
    
    def shuffle(self):
        random.shuffle(self._cards)

    def draw(self) -> Card | None: 
        if self._cards: #still cards in the deck
            self._deck_count -= 1
            return self._cards.pop() 
        else:  #no cards left
            return None # retur | Nonens the top card if such exist
    
    def lastCard(self):
        return len(self._cards) == 1
    
    def get_deck_count(self):
        return len(self._cards)