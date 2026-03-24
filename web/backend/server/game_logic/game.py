class Board() :
    def __init__(self, deck, piles, discards, token, misfires):
        self.deck = deck
        self.piles = piles
        self.discards = discards
        self.token = token
        self.misfires = misfires
    
    def canPlay(self, card):
        pass

    def play(Card):
        pass

    def calculateScore(self):
        pass

    def addToDiscard(self, card):
        pass

class Game:
    def __init__(self, id, board, players, currentTurn, state):
        self.id = id
        self.board = board
        self.players = players
        self.currentTurn = currentTurn
        self.state = state

    def playCard(self, player, card):
        pass   

    def giveHint(self, player, hint):
        pass

    def discardCard(self, player, card):
        pass

    def checkGameOver(self):
        pass
    