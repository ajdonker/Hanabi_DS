from web.backend.server.domain.cards import Color, Deck, HandCard, Number
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

    @property
    def token(self):
        return self.token

    def addDiscard(self, card):
        self.discards.append(card)
        
    def drawCard(self) -> HandCard :
        return self.deck.draw()

    def updateToken(self, mode : str):
        if(mode == '+'):
            if(self.token != 8): self.token += 1
        elif(mode == '-'):
            if(self.token == 0): raise NoTokenException()
            else : self.token -= 1
        else :
            pass #error

    def discardMisfire(self):
        self.misfires -= 1

    def updatePiles(self, card): #when a card is correctly played, the board is updated
        value = card.number
        color = card.color

        self.piles[color] = value

    def calculateScore(self): #calculate the score based on the piles in the board
        return sum(self.piles.values())

class Game():
    def __init__(self, gameID : int, board : Board, players : list[Player], playerTurn : int):
        self.gameID = gameID
        self.board = board
        self.players = players
        self.playerTurn = playerTurn #index of players list
    
    #-------------------Game actions-------------------#
    def playCard(self, username : str, cardIndex: int):

        self.canPlay(username) #check if it's player correct turn
        
        player = self.getPlayer(username)
        card = player.getCardByID(cardIndex)

        board = self.board
        color = card.color
        value = card.value
        
        player.removeCard(cardIndex)
        card.removeHints()  #remove hint

        if(board.piles[color] == 5) : #Corresponding pile is already full
            board.addDiscard(card)
            board.discardMisfire()
            raise ErrorException()  #to be catched in application layer

        if(value == board.piles[color] + 1) : #Card correctly placed
            board.updatePiles(card)
        else : # Wrong order --> mistake
            board.addDiscard(card)
            board.discardMisfire()
            raise ErrorException()
        
        #regardless the outcome of the action, the player must draw a card
        cardDrawn = board.drawCard() #update board
        player.addCard(cardDrawn)

        #check gameover
        
        #change turn
        self.changeTurn()


    def giveHint(self, username : str, cardIndex : list[int], hintType : str, value : str):
        
        self.canPlay(username, self.board)
         
        player = self.getPlayer(username)
        board = self.board        
        playerHand = player.getHand()

        if(hintType == "color"):
            hintColor = Color[value.upper()] #what if key it's not found ?
            for idx in cardIndex:
                playerHand[idx].setHintColor(hintColor)
                
        elif(hintType == "number"):
            hintNumber = Number(int(value)) #what if the string doesn't contain a number ?
            for idx in cardIndex:
                playerHand[idx].setHintNumber(hintNumber)
    
        else:
            raise UnknownHintTypeError()
        
        board.updateToken('-')
        
        #check gameover

        #change turn

    def discardCard(self, username : str, cardIndex: int):
                
        self.canPlay()
              
        player = self.getPlayer(username)
        card = player.getCardByID(cardIndex)
        board = self.board

        #remove hints
        card.removeHints()

        player.removeCard(cardIndex)
        board.addDiscard(card)

        #board update        
        board.updateToken('+')

        cardDrawn = board.drawCard() #update board
        player.addCard(cardDrawn)

        #change turn
        self.changeTurn()

        #check gameover

    #-------------------Utils-------------------#

    def canPlay(self, username : str, board : Board | None):
        if(username != self.playerTurn): 
            raise WrongTurnException() #to be catched in application layer (todo)

        elif(board.token == 0):
            raise NoTokenException() #to be catched in application layer (todo)

    def changeTurn(self):
        self.playerTurn = (self.playerTurn + 1) % len(self.players) 
        #return at the beginning of the list when is at the end

    def getPlayer(self, username): #gets a Player instance from his username
        for player in self.players :
            if player.username == username :
                return player
        
        raise UnknownError()

    def checkGameOver(self): #todo
        pass
