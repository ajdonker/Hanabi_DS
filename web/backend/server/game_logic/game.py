from web.backend.server.game_logic.cards import Deck
from web.backend.server.game_logic.player import Player

class Board() :
    def __init__(self, deck : Deck, piles : dict, discards : list, token : int, misfires : int):
        self.deck = deck
        self.piles = piles
        self.discards = discards
        self.token = token
        self.misfires = misfires

    @property
    def misfires(self):
        return self.misfires

    def addDiscard(self, card):
        self.discards.append(card)
        
        if(self.token != 8): #change as constant (?)
            self.token = self.token + 1

    def drawCard(self) :
        return self.deck.draw()

    def updateToken(self):
        pass

    def discardMisfire(self):
        self.misfires -= 1

    def updatePiles(self, card): #when a card is correctly played, the board is updated
        value = card.number
        color = card.color

        self.piles[color] = value

    def calculateScore(self): #calculate the score based on the piles in the board
        return sum(self.piles.values())

class Game():
    def __init__(self, gameID : int, board : Board, players : list, currentTurn : Player, state):
        self.gameID = gameID
        self.board = board
        self.players = players
        self.currentTurn = currentTurn
        self.state = state

    def getPlayer(self, playerID):
        pass

    def playCard(self, player, card) -> bool:
        
        if(player != self.currentTurn): #Not his turn (WRONG_TURN)
            return False
        
        board = self.board
        color = card.color
        value = card.value
        outcome = False

        if(board.piles[color] == 5) : # Error --> Corresponding pile is already full
            board.addDiscard(card)
            board.discardMisfire()

        if(value == board.piles[color] + 1) :
            outcome = True # Correct order
            board.updatePiles(card)
        else : # Wrong order --> mistake
            board.discardMisfire()
        
        #Regardless the outcome of the action, the player must draw a card
        cardDrawn = board.drawCard() #update board
        player.addCard(cardDrawn)

        return outcome

    def giveHint(self, player):
        pass

    def discardCard(self, player, card):
        pass

    def checkGameOver(self):
        pass
    