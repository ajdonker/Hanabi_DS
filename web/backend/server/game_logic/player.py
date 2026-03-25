

class Player:
    def __init__(self,id:str,name:str):
        self.id = id
        self.name = name
        self.hand = [None]*5
        self.hints = [[] for _ in range(5)]

    def clear_hints(self, card_idx: int):
        self.hints[card_idx] = [] # clear only that one which got discarded (not all)
    
    def addCard(self, card): 
        self.hand.append(card)
    
    def removeCard(self, card):
        if card in self.hand:
            self.hand.remove(card)
