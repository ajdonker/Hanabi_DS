import random
from enum import Enum
# 1 -> 3
# 2 -> 2
# 3 -> 2
# 4 -> 2
# 5 -> 1

class Color(Enum):
    RED, YELLOW, GREEN, BLUE, WHITE = range(5)

class Card():
    def __init__(self,number:int,color):
        self.number = number
        self.color = color

class Deck:
    def __init__(self):
        self.cards = []
        self.deck_count = 50 # 5 suits with 10 cards each 

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        if self.cards:
            self.deck_count -= 1
            return self.cards.pop() 
        else: 
            return None # returns the top card if such exist
    
    def isEmpty(self):
        return self.deck_count == 0