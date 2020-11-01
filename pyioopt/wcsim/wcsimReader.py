from pyioopt.core import reader, dataModel, geometry

from os import environ
from pathlib import Path

import numpy as np

import ROOT

class wcsimReader(reader.reader) :

    def __init__(self) :

        self.name = "wcsimReader"
        
        # Check if WCSim ROOT lib set up
        if environ.get('WCSIMDIR') == None :
            raise RuntimeError('WCSIMDIR not set')

        # Load WCSim ROOT library
        wcsimRootLib = list(Path(environ.get('WCSIMDIR')).glob('**/libWCSimRoot.so'))
        if len(wcsimRootLib) == 0 :
            wcsimRootLib = list(Path(environ.get('WCSIMDIR')).glob('**/libWCSimRoot.dylib'))
        if len(wcsimRootLib) == 0 :
            raise RuntimeError("Couldn't find libWCSimRoot in "+environ.get('WCSIMDIR'))

        ROOT.gSystem.Load(str(wcsimRootLib[0]))

        # Set up TChains
        self.eventChain = ROOT.TChain("wcsimT")
        self.geometryChain = ROOT.TChain("wcsimGeoT")
        
    def __getitem__(self, i) :
        if i < 0 or i > self.N :
            raise IndexError('Attempting to get {0}th event, but only have {1}.'.format(i, self.N))
        # Implement entry list for speed if i is list?
        self.eventChain.GetEntry(i)
        return wcsimEvent(self.eventChain.wcsimrootevent)
    
    def __len__ (self) :
        return self.N

    def addFile(self, fileName) :
        self.eventChain.Add(fileName)
        self.geometryChain.Add(fileName)
        self.N = self.eventChain.GetEntries()
        self.eventChain.GetBranch("wcsimrootevent").SetAutoDelete(ROOT.kTRUE)

class wcsimEvent(dataModel.event) :
    def __init__(self, wcsimRootEvent) :
        self.subEvents = []
        for iSubEvent in range(wcsimRootEvent.GetNumberOfEvents()) :
            self.subEvents.append(wcsimSubEvent(wcsimRootEvent.GetTrigger(iSubEvent)))

    def __getitem__(self, i) :
        return self.subEvents[i]

    def __len__(self) :
        return len(self.subEvents)

    def datetime(self) :
        return 0

    def eventNumber(self) :
        return 0

    def runNumber(self) :
        return 0

class wcsimSubEvent(dataModel.subEvent) :
    def __init__ (self, trigger) :
        nHits = trigger.GetNcherenkovdigihits()

        self._hits = np.zeros(nHits, dtype = [('PMT_number', np.uint32), ('q', np.float32), ('t', np.float32)])

        hits = trigger.GetCherenkovDigiHits()
        
        for i, hit in enumerate(hits) :
            self._hits[i] = (hit.GetTubeId(), hit.GetQ(), hit.GetT())

    def time(self) :
        return 0

    def trigger(self) :
        return 0

    def hits(self) :
        return self._hits
    
        
        
