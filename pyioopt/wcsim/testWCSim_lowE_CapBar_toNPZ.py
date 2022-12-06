#import pyioopt.wcsim.wcsim_reader
from wcsim import wcsim_reader

import numpy as np
import argparse
import os

def get_args():
    parser = argparse.ArgumentParser(description='dump WCSim data into numpy .npz file')
    parser.add_argument('-i',     '--input_files', type=str,   default = None, nargs = '+')
    parser.add_argument('-o',     '--outputdir',   type=str,   default = None)
    parser.add_argument('-l',     '--lower_limit', type=float, default = None)
    parser.add_argument('-u',     '--upper_limit', type=float, default = None)
    parser.add_argument('-n',     '--output_id',   type=int,   default = 0)
    parser.add_argument('-mode',  '--p_type',      type=str,   default = 'mu-')   #either 'mu-' or 'e-'
    args = parser.parse_args()
    return args

if __name__ == '__main__':

    config = get_args()

    mode = config.p_type
    E_uplimit = config.upper_limit
    E_lowlimit = config.lower_limit
    if mode == 'mu-':
        pid_label = 2.
    elif mode == 'e-':
        pid_label = 1.
    else:
        raise ValueError('invaild mode!')

    print("Events label: ", pid_label)

    infiles = []
    for f in config.input_files:
        if os.path.splitext(f)[1].lower() != '.root':
            print("File " + f + " is not a root file, skip it")
            continue
        f = os.path.abspath(f)
        infiles.append(f)
        
        
    if config.outputdir is not None:
        if not os.path.exists(config.outputdir):
            os.mkdir(config.outputdir)
        if not os.path.isdir(config.outputdir):
            raise argparse.ArgumentTypeError("Cannot access or create output directory" + config.outputdir)
        output_dir = config.outputdir
        print(output_dir)
        outfile = os.path.join(output_dir, "wcsimoutput_" + mode + "_" + str(E_lowlimit) + "_" + str(E_uplimit) + "_" + str(config.output_id)+".npz")
    else: 
        print("Output dir not specified, save the outputs in the same dir as input files.")
        outfile = os.path.splitext(infiles)[0] + '_wcsimoutput_'+ mode + '_' + str(E_lowlimit) + '_' + str(E_uplimit) + '_' + str(config.output_id)+'.npz'   

    print("Output file is: ", outfile)
        
    rd = wcsim_reader.Reader()
    print("Initialized reader")
    
    for f in infiles:
        rd.addFile(f)

    mask_top = rd.mask[0].astype(np.float32).flatten()
    mask_bottom = rd.mask[2].astype(np.float32).flatten()

    top = np.zeros(rd.mask[0].shape)
    barrel = np.zeros(rd.mask[1].shape)
    bottom = np.zeros(rd.mask[2].shape)

    print(rd.pmts())
    print('PMTs has been mapped.')

    #print("Counting events...")
    #for evt in rd:
    #    primary= [p for p in evt[0]["trueTracks"] if p["parenttype"]==0 and p["id"]==1 and p["E"] < E_uplimit and p["E"] > E_lowlimit ]
    #    events_num += len(primary)
    #print("Num of Events:", events_num, " with energy < ", E_uplimit )

    events_num = len(rd)
    directions = np.empty((events_num, 1, 3), dtype=np.float32)
    energies = np.empty((events_num, 1), dtype=np.float32)
    labels = np.empty((events_num, 1),dtype=np.float32)
    pids= np.empty((events_num, 1),dtype=np.float32)
    positions= np.empty((events_num, 1, 3),dtype=np.float32)
    event_data= np.empty((events_num, barrel.shape[0]*barrel.shape[1], 3), dtype =np.float32) #q, t, pmt
    event_data_top = np.empty((events_num, top.shape[0]*top.shape[1], 3), dtype = np.float32)
    event_data_bottom = np.empty((events_num, bottom.shape[0]*bottom.shape[1], 3),dtype = np.float32)

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
                        thisTop_pmt[rd.pmts()["column"][hit["pmtNumber"]-1], rd.pmts()["row"][hit["pmtNumber"]-1]] = hit["pmtNumber"]
                    elif rd.pmts()["location"][hit["pmtNumber"]-1] == 1 :
                        thisBarrel_q[rd.pmts()["column"][hit["pmtNumber"]-1], rd.pmts()["row"][hit["pmtNumber"]-1]] = hit['q']
                        thisBarrel_t[rd.pmts()["column"][hit["pmtNumber"]-1], rd.pmts()["row"][hit["pmtNumber"]-1]] = hit['t']
                        thisBarrel_pmt[rd.pmts()["column"][hit["pmtNumber"]-1], rd.pmts()["row"][hit["pmtNumber"]-1]] = hit["pmtNumber"]
                    elif rd.pmts()["location"][hit["pmtNumber"]-1] == 2 :
                        thisBottom_q[rd.pmts()["column"][hit["pmtNumber"]-1], rd.pmts()["row"][hit["pmtNumber"]-1]] = hit['q']
                        thisBottom_t[rd.pmts()["column"][hit["pmtNumber"]-1], rd.pmts()["row"][hit["pmtNumber"]-1]] = hit['t']
                        thisBottom_pmt[rd.pmts()["column"][hit["pmtNumber"]-1], rd.pmts()["row"][hit["pmtNumber"]-1]] = hit["pmtNumber"]
                        
                positions[iev] = vertex
                energies[iev] = evt_energy
                pids[iev] = evt_pid
                directions[iev] = evt_direction
                event_data[iev,:,0] = thisBarrel_q.flatten()
                event_data[iev,:,1] = thisBarrel_t.flatten()
                event_data[iev,:,2] = thisBarrel_pmt.flatten()
                event_data_top[iev,:,0] = thisTop_q.flatten()
                event_data_top[iev,:,1] = thisTop_t.flatten()
                event_data_top[iev,:,2] = thisTop_pmt.flatten()
                event_data_bottom[iev,:,0] = thisBottom_q.flatten()
                event_data_bottom[iev,:,1] = thisBottom_t.flatten()
                event_data_bottom[iev,:,2] = thisBottom_pmt.flatten()
                labels[iev] = pid_label # primitive setting
                
                del thisTop_q, thisTop_t, thisBarrel_q, thisBarrel_t, thisBottom_q, thisBottom_t                
                break # end of subevent loop with primary particle found
                
    np.savez_compressed(outfile, 
                        positions = positions,
                        energies = energies,
                        pids = pids,
                        directions = directions,
                        labels = labels,
                        event_data = event_data,
                        event_data_top = event_data_top,
                        event_data_bottom = event_data_bottom,
                        mask_top = mask_top,
                        mask_bottom = mask_bottom)
    
    print("Selected", j, " events, among which ", j - i, " are rejected by the Ecut.")

