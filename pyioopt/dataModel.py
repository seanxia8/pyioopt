from collections.abc import Sequence, Collection
from abc import ABC, abstractmethod

class pmt :
    def __init__(self, pmtType, pmtPosition, pmtDirection) :
        self.pmtType = pmtType
        self.pmtPos = pmtPos
        self.pmtDir = pmtDir

class hit :
    def __init__(self, pmtNumber, q, t) :
        self.pmtNumber = pmtNumber
        self.q = q
        self.t = t

class particle :
    def __init__(self, pdg, position, momentum, time):
        self.pdg = pdg
        self.position = position
        self.momentum = momentum
        self.time = time

class mcTruth(Collection, ABC) :
    @abstractmethod
    def __init__ (self) :
        pass

class subEvent(Sequence, ABC) :
    @abstractmethod
    def __init__(self) :
        pass

    @property
    @abstractmethod
    def time(self) :
        pass

    @property
    @abstractmethod
    def trigger(self) :
        pass
        
class event (Sequence, ABC) :

    @abstractmethod
    def __init__(self) :
        pass

    @property
    @abstractmethod
    def datetime(self):
        pass

    @property
    @abstractmethod
    def runNumber(self):
        pass

    @property
    @abstractmethod
    def eventNumber(self):
        pass
