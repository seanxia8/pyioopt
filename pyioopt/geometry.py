from collections.abc import Colleaction
from abc import ABC, abstractmethod

class detectorGeometry (Collection, ABC) :
    @abstractmethod
    def __init__(self) :
        pass

    @property
    @abstractmethod
    def pmts(self) :
        pass

class cylindricalDetector(detectorGeometry) :
    @property
    @abstractmethod
    def halfHeight(self) :
        pass

    @property
    @abstractmethod
    def radius(self) :
        pass
