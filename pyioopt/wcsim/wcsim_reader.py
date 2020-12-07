from pyioopt.core import reader, data_model, geometry

from os import environ
from glob import glob
from pathlib import Path

import numpy as np

import py_wcsim_reader

class Reader(reader.Reader, geometry.cylindricalDetector) :
    
    def __init__(self) :
        
        self._name = "wcsimReader"
        print("Initializing {0}".format(self._name))
        self._reader = py_wcsim_reader.py_wcsim_reader()
        self._geometryInit = False
        
    def __getitem__(self, i) :

        if i < 0 or i >= self._reader.N_events :
            raise IndexError('Attempting to get {0}th event, but only have {1}.'.format(i, self._reader.N_events))
        
        N_subevents = self._reader.loadEvent(i)

        subEvents = []

        for iSubEvent in range(N_subevents) :
            hits = self._reader.getHits(iSubEvent)
            trueTracks = self._reader.getTrueTracks(iSubEvent)
            vertex = self._reader.getVertex(iSubEvent)
            subEvents.append({"hits" : hits, "trueTracks" : trueTracks, "vertex" : vertex})

        return subEvents
    
    def __len__ (self) :
        return self._reader.N_events

    def addFile(self, fileName) :
        fileNames = glob(fileName)
        print(fileNames)
        print(len(fileNames))
        for f in fileNames :
            self._reader.addFile(f)
#            print("Adding file {0} events so far {1}".format(f, self._reader.N_events))
        self._pmts = self._reader.pmtInfo
            
        print("N events {0}".format(self._reader.N_events))
        if not self._geometryInit :
            self.fillRowColumn()
            self._radius = self._reader.cylinder_radius
            self._halfHeight = self._reader.cylinder_half_height


            
    def __contains__(self, m):
        return False
#    def __iter__(self) :
#        return self._pmts.__iter__
#    def __len__(self) :
#        return self._pmts.__len__
    def radius(self) :
        return self._radius
    def halfHeight(self) :
        return self._halfHeight
    def pmts(self) :
        return self._pmts


"""
class wcsimEvent(data_model.event) :
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

class wcsimSubEvent(data_model.subEvent) :
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
"""    

        
            
            
                                                            
