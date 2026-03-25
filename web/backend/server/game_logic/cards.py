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
    def __init__(self, card:Card, number:Number, color:Color):
        self.card = card
        self.hintColor = color
        self.hintNumber = number

class Deck():
    def __init__(self):
        self.cards = []
        self.count = 50 # 5 suits with 10 cards each 

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        if self.cards:
            self.count -= 1
            return self.cards.pop() 
        else: 
            return None # returns the top card if such exist
    
    def isEmpty(self):
        return self.deck_count == 0