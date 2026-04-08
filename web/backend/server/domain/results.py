class GameResult:
    def __init__(self):
        self.game_over = None | int
        self.next_player = None | str
    
    def setGameOver(self, score : int):
        self.game_over = score
    
    def setNextPlayer(self, next_player : str):
        self.next_player = next_player
        
class PlayDiscardCardResult(GameResult):
    def __init__(self):
        super().__init__(...)
        self.success = False
        self.misfire = 0
        self.score = None
    
    def setSuccess(self, success : bool):
        self.success = success
    
    def setMisfire(self, misfire : int):
        self.misfire = misfire
    

class HintResult(GameResult):
    def __init__(self):
        super().__init__(...)    
        self.tokensLeft = None | int

        