from web.backend.presentation.event import Event

class GameException(Exception):
    ###Base class for domain exceptions
    pass

#Managing the game

class KeyErrorException(GameException):
    pass

class GameNotFoundException(GameException):
    pass

###

class WrongTurnException(GameException): #It's not your turn
    pass

class NoTokenException(GameException): #No tokens left
    pass

class MisfireException(GameException): 
    pass

class InvalidCardException(GameException):
    pass

class InvalidHintException(GameException):
    pass

class UnknownErrorException(Exception):
    pass

class NoTokenException(Exception):
    pass


