class GameResult:
    def __init__(self):
        self.game_over: int | None = None
        self.next_player: str | None = None
        self.success: bool = False
    
    def setGameOver(self, score : int):
        self.game_over = score
    
    def setNextPlayer(self, next_player : str):
        self.next_player = next_player
        
    def setSuccess(self, success : bool):
        self.success = success
        
class PlayDiscardCardResult(GameResult):
    def __init__(self):
        super().__init__()
        self.misfire = 0
        self.drawn_card = None
        self.drawn_card_index: int | None = None

    def setMisfire(self, misfire : int):
        self.misfire = misfire

    def setDrawnCard(self, card, card_index: int):
        self.drawn_card = card
        self.drawn_card_index = card_index
    
class HintResult(GameResult):
    def __init__(self):
        super().__init__()    
        self.tokensLeft: int | None = None
    
    def setTokensLeft(self, tokens : int):
        self.tokensLeft = tokens

        
