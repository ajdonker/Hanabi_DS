class GameException(Exception):
    pass

class KeyErrorException(GameException):
    pass

class IndexError(GameException):
    pass

class GameNotFoundException(GameException):
    pass

class WrongTurnException(GameException): #It's not your turn
    pass

class NoTokenException(GameException):
    pass

class MisfireException(GameException):
    pass

###################


class LobbyException(Exception):
    pass

