from core import reader, data_model, geometry

from os import environ
from glob import glob
from pathlib import Path

import numpy as np
import py_wcsim_reader

def prepare_inputs(inputlist):
    infiles = []
    for f in inputlist:
        if os.path.splitext(f)[1].lower() != '.root':
            print("File " + f + " is not a root file, skip it")
            continue
        f = os.path.abspath(f)
        infiles.append(f)
    return infiles    

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

def initialize_h5(output_file, nevents, num_top, num_barrel, num_bottom):
    with h5py.File(output_file,'w') as f:
        f.attrs['CLASS'] = np.array('GROUP', dtype='S')
        f.attrs['TITLE'] = np.array('', dtype='S')
        f.attrs['FILTERS'] = 65797
        f.attrs['PYTABLES_FORMAT_VERSION'] = np.array('2.1', dtype='S')
        f.attrs['VERSION'] = np.array('1.0', dtype='S')

        f.create_dataset("directions", shape=(nevents, 1, 3), dtype=np.float32, maxshape=(nevents, 1, 3), compression="gzip", compression_opts=5, shuffle=True)
        f.create_dataset("energies", shape=(nevents, 1), dtype=np.float32, maxshape=(nevents, 1), compression="gzip", compression_opts=5, shuffle=True)
        f.create_dataset("labels", shape=(nevents, 1), dtype=np.float32, maxshape=(nevents, 1), compression="gzip", compression_opts=5, shuffle=True)
        f.create_dataset("pids", shape=(nevents, 1), dtype=np.float32, maxshape=(nevents, 1), compression="gzip", compression_opts=5, shuffle=True)
        f.create_dataset("positions", shape=(nevents, 1, 3), dtype=np.float32, maxshape=(nevents, 1, 3), compression="gzip", compression_opts=5, shuffle=True)

        f.create_dataset("event_data_barrel", shape=(nevents*num_barrel, 2), dtype=np.float32, maxshape=(nevents*num_barrel, 2), compression="gzip", compression_opts=5, shuffle=True)
        f.create_dataset("event_data_top", shape=(nevents*num_top, 2), dtype=np.float32, maxshape=(nevents*num_top, 2), compression="gzip", compression_opts=5, shuffle=True)
        f.create_dataset("event_data_bottom", shape=(nevents*num_bottom, 2), dtype=np.float32, maxshape=(nevents*num_bottom, 2),  compression="gzip", compression_opts=5, shuffle=True)
        
        f.create_dataset("hit_index_barrel", shape=(nevents*num_barrel,1), dtype=np.int32,
                         maxshape=(nevents*num_barrel,1),
                         compression="gzip", compression_opts=5, shuffle=True)

        f.create_dataset("hit_index_top", shape=(nevents*num_top,1), dtype=np.int32,
                         maxshape=(nevents*num_top,1),
                         compression="gzip", compression_opts=5, shuffle=True)
        f.create_dataset("hit_index_bottom", shape=(nevents*num_bottom,1), dtype=np.int32,
                         maxshape=(nevents*num_bottom,1),
                         compression="gzip", compression_opts=5, shuffle=True)
        f.create_dataset("nhit_barrel", shape=(nevents, 2), dtype=np.int32,
                         maxshape=(nevents, 2),
                         compression="gzip", compression_opts=5, shuffle=True)
        f.create_dataset("nhit_top", shape=(nevents, 2), dtype=np.int32,
                         maxshape=(nevents, 2),
                         compression="gzip", compression_opts=5, shuffle=True)
        f.create_dataset("nhit_bottom", shape=(nevents, 2), dtype=np.int32,
                         maxshape=(nevents, 2),
                         compression="gzip", compression_opts=5, shuffle=True)

        for dataset_name in f.keys():
            dataset = f.get(dataset_name)
            if dataset_name != "labels":
                dataset.attrs['CLASS']=np.array('EARRAY',dtype='S')
                dataset.attrs['TITLE']=np.array('',dtype='S')
                dataset.attrs['VERSION']=np.array('1.1', dtype='S')
                dataset.attrs['EXTDIM'] =np.int32(0)
            else:
                dataset.attrs['CLASS'] = np.array('CARRAY',dtype = 'S')
                dataset.attrs['TITLE'] = np.array('',dtype='S')
                dataset.attrs['VERSION']=np.array('1.1', dtype='S')
        
        return f

def extract_root(rd, nevents, top, barrel, bottom):
    directions = np.empty((nevents, 1, 3), dtype=np.float32)
    energies = np.empty((nevents, 1), dtype=np.float32)
    labels = np.empty((nevents, 1),dtype=np.float32)
    pids= np.empty((nevents, 1),dtype=np.float32)
    positions= np.empty((nevents, 1, 3),dtype=np.float32)
    event_data= np.empty((nevents, barrel.shape[0]*barrel.shape[1], 2), dtype =np.float32) #q, t                
    event_data_top = np.empty((nevents, top.shape[0]*top.shape[1], 2), dtype = np.float32)
    event_data_bottom = np.empty((nevents, bottom.shape[0]*bottom.shape[1], 2),dtype = np.float32)

    i = 0
    j = 0
    for iev, event in enumerate(rd) :
        if iev % 100 == 0:
            print("EVENT {0}".format(iev))

        for isub, sub in enumerate(event) :
            if iev % 100 == 0:
                print ("SUB-EVENT {0}".format(isub))
            particles = [t for t in sub["trueTracks"] if t["parenttype"]==0 and t["id"] == 1]
            if len(particles) == 1:
                evt_energy = particles[0]["E"]
                evt_pid = particles[0]["PDG_code"]
                direction = [particles[0]["dirx"], particles[0]["diry"], particles[0]["dirz"]]
                evt_direction = np.array(direction).reshape(1,3)
                vertex = sub["vertex"].copy()
                vertex = vertex.view('<f4').reshape(1,3)
                j += 1
                if evt_energy < E_uplimit and evt_energy > E_lowlimit:
                    i += 1
                else:
                    continue
                thisTop_q = np.copy(top).astype(float)
                thisTop_t = np.copy(top).astype(float)
                thisTop_pmt = np.copy(top).astype(int)

                thisBarrel_q = np.copy(barrel).astype(float)
                thisBarrel_t = np.copy(barrel).astype(float)
                thisBarrel_pmt = np.copy(barrel).astype(int)

                thisBottom_q = np.copy(bottom).astype(float)
                thisBottom_t = np.copy(bottom).astype(float)
                thisBottom_pmt = np.copy(bottom).astype(int)
                
                for hit in sub["hits"] :
                    if rd.pmts()["location"][hit["pmtNumber"]-1] == 0 :
                        thisTop_q[rd.pmts()["column"][hit["pmtNumber"]-1], rd.pmts()["row"][hit["pmtNumber"]-1]] = hit['q']
                        thisTop_t[rd.pmts()["column"][hit["pmtNumber"]-1], rd.pmts()["row"][hit["pmtNumber"]-1]] = hit['t']
                    elif rd.pmts()["location"][hit["pmtNumber"]-1] == 1 :
                        thisBarrel_q[rd.pmts()["column"][hit["pmtNumber"]-1], rd.pmts()["row"][hit["pmtNumber"]-1]] = hit['q']
                        thisBarrel_t[rd.pmts()["column"][hit["pmtNumber"]-1], rd.pmts()["row"][hit["pmtNumber"]-1]] = hit['t']
                    elif rd.pmts()["location"][hit["pmtNumber"]-1] == 2 :
                        thisBottom_q[rd.pmts()["column"][hit["pmtNumber"]-1], rd.pmts()["row"][hit["pmtNumber"]-1]] = hit['q']
                        thisBottom_t[rd.pmts()["column"][hit["pmtNumber"]-1], rd.pmts()["row"][hit["pmtNumber"]-1]] = hit['t']

                positions[iev] = vertex
                energies[iev] = evt_energy
                pids[iev] = evt_pid
                directions[iev] = evt_direction
                event_data[iev,:,0] = thisBarrel_q.flatten()
                event_data[iev,:,1] = thisBarrel_t.flatten()

                event_data_top[iev,:,0] = thisTop_q.flatten()
                event_data_top[iev,:,1] = thisTop_t.flatten()

                event_data_bottom[iev,:,0] = thisBottom_q.flatten()
                event_data_bottom[iev,:,1] = thisBottom_t.flatten()

                labels[iev] = pid_label # primitive setting

                del thisTop_q, thisTop_t, thisBarrel_q, thisBarrel_t, thisBottom_q, thisBottom_t
                break # end of subevent loop with primary particle found

    
    
