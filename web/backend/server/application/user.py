from dataclasses import dataclass
import hashlib
  
class User:
    def __init__(self,fullName: str, username: str, email: str, password: str):
        self._fullName = fullName
        self._username = username
        self._email = email 
        self._hashedPass = hashlib.sha256(password.encode('utf-8')).hexdigest() 
        #hashed with sha-256

    @property
    def hashedpass(self):
        return self._hashedPass