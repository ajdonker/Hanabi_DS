from server.domain.cards import Color, Deck, HandCard, Number, Card
from server.domain.player import Player
from server.domain.exceptions import *
from typing import List 
from server.domain.gameInterface import GameInterface

class Board() :
    def __init__(self, deck : Deck, piles : dict, discards : list, token : int, misfires : int):
        self._deck = deck
        self._piles = piles
        self._discards = discards
        self._token = token
        self._misfires = misfires

    #getters
    @property
    def misfires(self):
        return self._misfires 

    @property
    def token(self):
        return self._token
    
    @property
    def piles(self):
        return self._piles

    @property
    def deck(self):
        return self._deck
    
    @property
    def discards(self):
        return self._discards

    def addDiscard(self, card): #add a card to discard pile
        self._discards.append(card)
        
    def drawCard(self) -> HandCard | None : #draw a card (if possible)
        return self._deck.draw()

    def updateToken(self, mode : str): #update Token based on the move
        if(mode == '+'):
            if(self._token < 8): self._token += 1
        elif(mode == '-'):
            if(self._token == 0): raise NoTokenException()
            else : self._token -= 1
        else :
            raise UnknownErrorException()

    def discardMisfire(self):
        self._misfires -= 1

    def updatePiles(self, card): #when a card is correctly played, the board is updated
        value = card.number.value
        color = card.color 
        self._piles[color] = value # where is the check on correct 

    #a gameover condition
    def completedPiles(self):
        return all(v == 5 for v in self._piles.values())        
        #return all(height == Number.FIVE.value for height in self._piles.values())  alternative

    def calculateScore(self): #calculate the score based on the piles in the board
        return sum(self._piles.values())

class Game(GameInterface):
    def __init__(self, gameID : int, board : Board, players : list[Player], playerTurn : str):

        self._gameID = gameID
        self._board = board
        self._players = {p._username: p for p in players} #create a dict for quick access {"username" : Player obj}
        self._turnOrder = [p._username for p in players] #list of usernames in the order of the turns
        self._playerTurn = playerTurn 
        self._finalTurn = False

    @property
    def gameID(self) -> int:
        return self._gameID
    
    @property
    def board(self) -> Board:
        return self._board
    
    @property
    def players(self) -> dict[str, Player]:
        return self._players
    
    @property
    def turnOrder(self) -> list[str]:
        return self._turnOrder
    
    @property
    def playerTurn(self) -> str:
        return self._playerTurn
    
    @property
    def finalTurn(self) -> bool:
        return self._finalTurn

    def setFinalTurn(self,turn : bool):
        self._finalTurn = turn
        
    def getPlayer(self, username: str) -> Player:

        if username not in self._players:
            raise KeyError(f"Player {username} not found")
        
        return self._players[username]
    
    @staticmethod
    def _create_initial_game(game_id:int = 0, player_names: List[str] = ["Player1","Player2"]):
        players = [Player(name) for name in player_names]

        deck = Deck()
        deck.shuffle()

        # deal cards
        for p in players:
            for _ in range(5):  # or 4 depending on rules
                p.addCard(HandCard(deck.draw()))

        board = Board(
            deck=deck,
            piles={c: 0 for c in Color},
            discards=[],
            token=8,
            misfires=3
        )

        return Game(
            gameID=game_id,
            board=board,
            players=players,
            playerTurn=player_names[0]
        )
    
    #-------------------Game actions-------------------#
    def playCard(self, username : str, cardIndex: int):

        self.canPlay(username) #check if player can actually play
        
        player = self._players[username]
        card = player.getCardByID(cardIndex)

        board = self._board
        color = card.color
        value = card.number.value
        
        player.removeCard(cardIndex)
        card.removeHints()  #remove hint

        exc = False

        if(board._piles[color] == 5) : #Corresponding pile is already full
            board.addDiscard(card)
            board.discardMisfire()
            exc = True
            #raise MisfireException()  #to be catched in application layer

        if(value == board._piles[color] + 1) : #Card correctly placed
            board.updatePiles(card)
        else : # Wrong order --> mistake
            board.addDiscard(card)
            board.discardMisfire()
            #raise MisfireException()
            exc = True
        
        #check gameover
        self.checkGameOver()
        
        #unless game is over, the player must draw a card (regardless of his action)
        cardDrawn = board.drawCard() #update board
        if(board._deck.get_deck_count() <= 1): 
            self._finalTurn = True
            player.setLastTurn(True)
        
        if(cardDrawn != None): player.addCard(HandCard(cardDrawn))
        
        self.checkGameOver()
        
        #change turn
        self.changeTurn()
        if exc:
            raise MisfireException()

    def giveHint(self, username: str, target: str, *, color: Color = None, number: Number = None):

        board = self._board

        invalid = (
            (color is None and number is None) or
            (color is not None and number is not None) or
            (username == target) or
            (board._token == 0)
        )

        self.canPlay(username)

        player = self.getPlayer(target)
        playerHand = player.getHand

        matched = False

        if not invalid:
            for card in playerHand:
                if color is not None:
                    if card.card.color == color:
                        card.setHintColor(color)
                        matched = True

                elif number is not None:
                    if card.card.number == number:
                        card.setHintNumber(number)
                        matched = True

        success = (not invalid) and matched

        board.updateToken('-')

        self.checkGameOver()
        self.changeTurn()

        if (not success):
            raise InvalidHintException

    def discardCard(self, username : str, cardIndex: int):
                    
        self.canPlay(username)
              
        player = self.getPlayer(username)
        card = player.getCardByID(cardIndex)
        board = self._board

        card.removeHints()
        player.removeCard(cardIndex)
        board.addDiscard(card)

        board.updateToken('+')

        cardDrawn = board.drawCard() 
        if(board._deck.get_deck_count() < 1): 
            self._finalTurn = True
            player.setLastTurn(True)
            
        if(cardDrawn != None): player.addCardAt(cardIndex,HandCard(cardDrawn))
        print("AFTER INSERT:", [id(c) for c in player._hand])

        self.checkGameOver()
        
        self.changeTurn()

    #-------------------Utils-------------------#

    def canPlay(self, username : str):
        
        if(username != self._playerTurn): 
            raise WrongTurnException() #to be catched in application layer (done)

        elif(self.board.token == 0):
            raise NoTokenException() #to be catched in application layer (todo)
        
        elif(self.finalTurn): #can play, but it's his last turn
            self._players[username].setLastTurn(True)
        

    def changeTurn(self):
        
        playerTurn = self._playerTurn 
        
        currentPlayerIndex = self._turnOrder.index(playerTurn)
        nextPlayerIndex = (currentPlayerIndex + 1) % len(self._players) #return at the beginning of the list when is at the end
        self._playerTurn = self._turnOrder[nextPlayerIndex]
        
        if(self._finalTurn):
            self._players[playerTurn].setLastTurn(True)
        
    def checkGameOver(self) -> int | None: 
        
        if self._board._misfires == 0:
            return self._board.calculateScore()

        if self._board.completedPiles():
            return self._board.calculateScore()

        if all(p._lastTurn for p in self._players.values()):
            return self._board.calculateScore()

        return None
    
    def debugPrintState(self):
        print("\n" + "="*60)
        print(f"GAME DEBUG STATE (GameID: {self._gameID})")
        print("="*60)

        # --- Turn Info ---
        print("\n--- TURN INFO ---")
        print(f"Current Player Turn: {self._playerTurn}")
        print(f"Turn Order: {self._turnOrder}")
        print(f"Final Turn Active: {self._finalTurn}")

        # --- Board ---
        board = self._board
        print("\n--- BOARD ---")
        print(f"Tokens: {board._token}")
        print(f"Misfires (lives): {board._misfires}")
        print(f"Piles: {board._piles}")
        print(f"Discard pile size: {len(board._discards)}")
        print(f"Deck size: {len(board._deck._cards)}")

        # --- Players ---
        print("\n--- PLAYERS ---")
        for username in self._turnOrder:  # preserves actual turn order
            player = self._players[username]

            print(f"\nPlayer: {username}")
            print(f"  Last Turn Flag: {player._lastTurn}")

            print("  Hand:")
            for i, handCard in enumerate(player._hand):
                card = handCard.card

                # safe hint access
                hint_color = getattr(handCard, "_hintColor", None)
                hint_number = getattr(handCard, "_hintNumber", None)

                print(
                    f"    [{i}] "
                    f"{card.color}-{card.number} | "
                    f"Hints -> color: {hint_color}, number: {hint_number} | "
                    f"HandCardID: {id(handCard)} CardID: {id(card)}"
                )

        print("\n" + "="*60 + "\n")