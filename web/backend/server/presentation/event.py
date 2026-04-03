class Event() :
    def __init__(self,type:str, data:dict[str, object]):
        self.type = type
        self.data = data