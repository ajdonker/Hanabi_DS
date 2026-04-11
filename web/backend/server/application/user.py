from dataclasses import dataclass
import hashlib
  
class User:
    def __init__(self,fullName: str, username: str, email: str, password: str):
        self._fullName = fullName
        self._username = username
        self._email = email 
        self._hashedPass = hashlib.sha256(password.encode('utf-8')).hexdigest() 
        #hashed with sha-256

    @staticmethod
    def from_dict(data : dict, username : str):
        user = User.__new__(User) 
        user._fullName = data["fullName"]
        user._username = username
        user._email = data["email"]
        user._hashedPass = data["password"]
        return user
    
    @staticmethod
    def to_dict(user : 'User') -> dict:
        return {
            "fullName": user._fullName,
            "email": user._email,
            "password": user._hashedPass
        }