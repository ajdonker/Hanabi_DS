from web.backend.server.game_logic import cards
from web.backend.server.game_logic import Deck

class Board() :
    def __init__(self, deck : Deck, piles : dict, discards : list, token : int, misfires : int):
        self.deck = deck
        self.piles = piles
        self.discards = discards
        self.token = token
        self.misfires = misfires

    def addDiscard(self, card): 
        self.discards.append(card)
        
        if(self.token != 8): #change as constant (?)
            self.token = self.token + 1

    def updatePiles(self, card): #when a card is correctly played, the board is updated
        value = card.number
        color = card.color

        self.piles[color] = value

    def calculateScore(self): #calculate the score based on the piles in the board
        return sum(self.piles.values())

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
    