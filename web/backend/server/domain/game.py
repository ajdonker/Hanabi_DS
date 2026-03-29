from web.backend.server.domain.cards import Color, Deck, HandCard, Number
from web.backend.server.domain.player import Player

class Board() :
    def __init__(self, deck : Deck, piles : dict, discards : list, token : int, misfires : int):
        self.deck = deck
        self.piles = piles
        self.discards = discards
        self.token = token
        self.misfires = misfires

    #getters
    @property
    def misfires(self):
        return self.misfires

    @property
    def token(self):
        return self.token

    def addDiscard(self, card): #add a card to discard pile
        self.discards.append(card)
        
    def drawCard(self) -> HandCard | None : #draw a card (if possible)
        return self.deck.draw()

    def updateToken(self, mode : str): #update Token based on the move
        if(mode == '+'):
            if(self.token != 8): self.token += 1
        elif(mode == '-'):
            if(self.token == 0): raise NoTokenException()
            else : self.token -= 1
        else :
            raise UnknownErrorException()

    def discardMisfire(self):
        self.misfires -= 1

    def updatePiles(self, card): #when a card is correctly played, the board is updated
        value = card.number
        color = card.color

        self.piles[color] = value

    #a gameover condition
    def completedPiles(self):
        if(self.calculateScore() == 25): return True        
        #return all(height == Number.FIVE.value for height in self.piles.values())  alternative

    def calculateScore(self): #calculate the score based on the piles in the board
        return sum(self.piles.values())

class Game():
    def __init__(self, gameID : int, board : Board, players : list[Player], playerTurn : str):
        self.gameID = gameID
        self.board = board
        self.players = {p.username: p for p in players} #create a dict for quick access {"username" : Player obj}
        self.turnOrder = [p.username for p in players] #list of usernames in the order of the turns
        self.playerTurn = playerTurn 
        self.finalTurn = False
        
    #-------------------Game actions-------------------#
    def playCard(self, username : str, cardIndex: int):

        self.canPlay(username) #check if player can actually play
        
        player = self.players[username]
        card = player.getCardByID(cardIndex)

        board = self.board
        color = card.color
        value = card.value
        
        player.removeCard(cardIndex)
        card.removeHints()  #remove hint

        if(board.piles[color] == 5) : #Corresponding pile is already full
            board.addDiscard(card)
            board.discardMisfire()
            raise MisfireException()  #to be catched in application layer

        if(value == board.piles[color] + 1) : #Card correctly placed
            board.updatePiles(card)
        else : # Wrong order --> mistake
            board.addDiscard(card)
            board.discardMisfire()
            raise MisfireException()
        
        #check gameover
        self.checkGameOver()
        
        #unless game is over, the player must draw a card (regardless of his action)
        cardDrawn = board.drawCard() #update board
        if(board.deck.lastCard): self.finalTurn = True
        
        if(cardDrawn != None): player.addCard(cardDrawn)
        
        self.checkGameOver()
        
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
            raise UnknownErrorException()
        
        board.updateToken('-')
        
        #check gameover
        self.checkGameOver()

        #change turn
        self.changeTurn()

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
        if(board.deck.lastCard): self.finalTurn = True
        
        if(cardDrawn != None): player.addCard(cardDrawn)
        
        #check gameover
        self.checkGameOver()
        
        #change turn
        self.changeTurn()

    #-------------------Utils-------------------#

    def canPlay(self, username : str, board : Board | None):
        
        if(username != self.playerTurn): 
            raise WrongTurnException() #to be catched in application layer (done)

        elif(board.token == 0):
            raise NoTokenException() #to be catched in application layer (todo)
        
        elif(self.finalTurn): #can play, but it's his last turn
            self.players[username].setLastTurn(True)
        

    def changeTurn(self):
        
        playerTurn = self.playerTurn 
        
        currentPlayerIndex = self.turnOrder.index(playerTurn)
        nextPlayerIndex = (currentPlayerIndex + 1) % len(self.players) #return at the beginning of the list when is at the end
        playerTurn = self.turnOrder[nextPlayerIndex]
        
        if(self.finalTurn):
            self.players[playerTurn].setLastTurn(True)
        
    def checkGameOver(self) -> int | None: 
        
        if(self.board.misfires == 0): #no misfires left
            return self.board.calculateScore()
        elif(self.board.completedPiles): #all piles completed
            return self.board.calculateScore()
        elif all(player.lastTurn for player in self.players_map.values()): #all player made their last move
            return self.board.calculateScore()
        
        #Game continues
        return None
        