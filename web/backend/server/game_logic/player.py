

class Player():
    def __init__(self, id:str, name:str, hand:list):
        self.id = id
        self.name = name
        self.hand = [None]*5
    
    def addCard(self, card): 
        self.hand.append(card)
    
    def removeCard(self, card):
        if card in self.hand:
            self.hand.remove(card)
    
