class GameResult:
    def __init__(self):
        self.game_over = None | int
        self.next_player = None | str
        self.success = False
    
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

    def setMisfire(self, misfire : int):
        self.misfire = misfire
    
class HintResult(GameResult):
    def __init__(self):
        super().__init__()    
        self.tokensLeft = None | int
    
    def setTokensLeft(self, tokens : int):
        self.tokensLeft = tokens

        