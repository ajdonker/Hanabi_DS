from dataclasses import dataclass

@dataclass
class User:
    fullName: str
    username: str
    email: str
    password: str