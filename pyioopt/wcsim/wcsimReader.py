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

        # Geometry is read in when first file gets added
        self.geometry = None
        
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
        self.N = self.eventChain.GetEntries()
        self.eventChain.GetBranch("wcsimrootevent").SetAutoDelete(ROOT.kTRUE)

        if self.geometry == None :
            self.geometryChain.Add(fileName)
            self.geometry = wcsimGeometry(self.geometryChain)

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

        nTrueTracks = trigger.GetNtrack()
        self._trueTracks = np.zeros(nTrueTracks, dtype = [('PDG_code', np.uint32), ('m', np.float32), ('p', np.float32), ('E', np.float32), ('startvol', np.int32), ('stopvol', np.int32), ('dir_x', np.float32), ('dir_y', np.float32), ('dir_z', np.float32), ('stop_x', np.float32), ('stop_y', np.float32), ('stop_z', np.float32), ('start_x', np.float32), ('start_y', np.float32), ('start_z', np.float32), ('parenttype', np.int32), ('time', np.float32), ('id', np.int32)])

        for i, track in enumerate(trigger.GetTracks()) :
            self._trueTracks = (track.GetIpnu(), track.GetM(), track.GetP(), track.GetE(), track.GetStartvol(), track.GetStopvol(), track.GetDir(0), track.GetDir(1), track.GetDir(2), track.GetStop(0), track.GetStop(1), track.GetStop(2), track.GetStart(0), track.GetStart(1), track.GetStart(2), track.GetParenttype(), track.GetTime(), track.GetId())

    def time(self) :
        return 0
    def trigger(self) :
        return 0
    def hits(self) :
        return self._hits
    def trueTracks(self) :
        return self._trueTracks
    
class wcsimGeometry(geometry.cylindricalDetector) :
    def __init__(self, geometryChain) :
        geometryChain.GetEntry(0)
        thisGeo = geometryChain.wcsimrootgeom
        self.N_PMT = thisGeo.GetWCNumPMT()
        self._radius = thisGeo.GetWCCylRadius()
        self._halfHeight = thisGeo.GetWCCylLength()

        self._pmts = np.zeros(self.N_PMT, dtype = [('x', np.float32), ('y', np.float32), ('z', np.float32), ('dir_x', np.float32), ('dir_y', np.float32), ('dir_z', np.float32), ('location', np.uint8), ('row', np.uint16), ('column', np.uint16)])

        for iPMT in range(self.N_PMT) :
            this_pmt = thisGeo.GetPMTPtr(iPMT)
            
            self._pmts[iPMT] = (this_pmt.GetPosition(0),
                                this_pmt.GetPosition(1),
                                this_pmt.GetPosition(2),
                                this_pmt.GetOrientation(0),
                                this_pmt.GetOrientation(1),
                                this_pmt.GetOrientation(2),
                                this_pmt.GetCylLoc(),
                                0, 0)


        self.fillRowColumn()

    def __contains__(self, m):
        return False
    def __iter__(self) :
        return self._pmts.__iter__
    def __len__(self) :
        return self._pmts.__len__
    def radius(self) :
        return self._radius
    def halfHeight(self) :
        return self._halfHeight
    def pmts(self) :
        return self._pmts
        
            
            
                                                            
