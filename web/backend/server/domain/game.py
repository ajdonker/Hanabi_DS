from web.backend.server.domain.cards import Deck, HandCard
from web.backend.server.domain.player import Player

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

    def drawCard(self) -> HandCard :
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
    def __init__(self, gameID : int, board : Board, players : list[Player], playerTurn : int, state):
        self.gameID = gameID
        self.board = board
        self.players = players
        self.playerTurn = playerTurn
        self.state = state
    
    # game actions
    def playCard(self, playerID : int, cardIndex: int):

        if(playerID != self.currentTurn): 
            raise WrongTurnException() #to be catched in application layer
        
        player = self.getPlayer(playerID)
        card = player.getCard(cardIndex)

        board = self.board
        color = card.color
        value = card.value
        
        if(board.piles[color] == 5) : #Corresponding pile is already full
            board.addDiscard(card)
            board.discardMisfire()
            raise ErrorException()  #to be catched in application layer

        if(value == board.piles[color] + 1) : #Card correctly placed
            board.updatePiles(card)
        else : # Wrong order --> mistake
            board.discardMisfire()
            raise ErrorException()
        
        #remove hint (?)

        #regardless the outcome of the action, the player must draw a card
        cardDrawn = board.drawCard() #update board
        player.addCard(cardDrawn)

        #change turn
        self.changeTurn()

        #check gameover


    def giveHint(self, playerIDFrom : int, playerIDTo : int, cardIndex : list[int], hintType : str, value : str  ):
        
        if(playerIDFrom != self.currentTurn): 
            raise WrongTurnException() #to be catched in application layer
         
        playerFrom = self.getPlayer(playerIDFrom)
        playerTo = self.getPlayer(playerIDTo)
        board = self.board
        
        playerToHand = playerTo.getHand()
        #todo logic of give hint

        if(hintType == "color"):
            pass
        elif(hintType == "number"):
            pass
        else:
            raise UnknownHintTypeError()


    def discardCard(self, playerID : int, cardIndex: int):
                
        if(playerID != self.currentTurn): 
            raise WrongTurnException() #to be catched in application layer
              
        player = self.getPlayer(playerID)
        card = player.getCard(cardIndex)
        board = self.board

        #remove hint (?)

        player.removeCard(card)
        board.addDiscard(card)
        
        #regardless the outcome of the action, the player must draw a card
        cardDrawn = board.drawCard() #update board
        player.addCard(cardDrawn)

        #change turn
        self.changeTurn()

        #check gameover

    #utils

    def changeTurn(self): #todo
        pass
        
    def getPlayer(self, playerID): #gets a Player instance from his ID
        for player in self.players :
            if player.playerID == playerID :
                return player

        raise UnknownError()

    def checkGameOver(self):
        pass
    