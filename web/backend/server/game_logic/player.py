class Player:
    def __init__(self, id, name, hand):
        self.id = id
        self.name = name
        self.hand = []
    
    def addCard(self, card): 
        self.hand.append(card)
    
    def removeCard(self, card):
        if card in self.hand:
            self.hand.remove(card)
