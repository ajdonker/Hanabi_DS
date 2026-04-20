from abc import ABC,abstractmethod

class IHandler(ABC):
        
    @abstractmethod
    def execute(self,msg):
        pass
