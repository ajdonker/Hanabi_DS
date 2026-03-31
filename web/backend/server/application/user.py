
class User:
    def __init__(self,fullName: str, username: str, email: str, hashedPass: str):
        self._fullName = fullName
        self._username = username
        self._email = email 
        self._hashedPass = hashedPass