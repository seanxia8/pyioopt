from collections.abc import Sequence
from abc import ABC, abstractmethod

class reader (Sequence, ABC) :
    def __init__(self) :
        pass

    @abstractmethod
    def addFile(self) :
        pass
