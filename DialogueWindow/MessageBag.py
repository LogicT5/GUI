from enum import Enum, auto

class Role(Enum):
    User = auto()
    Other = auto()

class MessageBag:
    def __init__(self,role:Role,text:str):
        self.role:Role = role
        self.text:str = text