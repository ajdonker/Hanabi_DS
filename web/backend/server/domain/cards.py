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
        self.number = number
        self.color = color
    
    #getters
    @property 
    def number(self):
        return self.number
    
    @property 
    def color(self):
        return self.color

class HandCard():
    def __init__(self, card:Card):
        self.card = card
        self.hintColor = Color | None
        self.hintNumber = Color | None
    
    @property 
    def card(self):
        return self.card
    
    def setHintColor(self, color:Color):
        self.hintColor = color

    def setHintNumber(self, number:Number):
        self.hintNumber = number

    def removeHints(self):
        self.hintColor = None
        self.hintNumber = None

class Deck():
    def __init__(self):
        self.cards = [None]*50 

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        if self.cards: #still cards in the deck
            self.count -= 1
            return self.cards.pop() 
        else:  #no cards left
            return None # returns the top card if such exist
    
    def lastCard(self):
        return self.cards.count == 1