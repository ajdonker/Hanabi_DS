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
    def __repr__(self): # returns printable representation of the card 
        return f"Card({self.number}, {self.color.name})"
class Deck:
    def __init__(self):
        # counts: 1→3, 2→2, 3→2, 4→2, 5→1
        counts = {1:3, 2:2, 3:2, 4:2, 5:1}
        self.cards = [
            Card(num, col)
            for num, cnt in counts.items()
            for col in Color
            for _ in range(cnt)
        ] # list of cards in each number and color 
        self.deck_count = 50 # 5 suits with 10 cards each 

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        if self.cards:
            self.deck_count -= 1
            return self.cards.pop() 
        else: 
            return None # returns the top card if such exists
    def get_deck_count(self):
        return self.deck_count
# 5 cards to 2 or 3 players 
# 4 cards to 4 or 5 players 

# broadcast game state to all players and then the client of the player "censors" the players own cards
# or broadcast separately without his own cards 
# player info sent with each mess on his own cards : card idx 1,2,3 - know green,4 - know its a 2 
# complete state of the game is - no cards in deck,all player cards, the 5 towers in the middle, the token state, 
# game ends if 3 times mess up order / color , all 5 towers are made succ, or all cards played