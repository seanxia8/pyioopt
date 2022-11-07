import wcsim_reader

import numpy as np
import argparse
import os

def get_args():
    parser = argparse.ArgumentParser(description='dump WCSim data into numpy .npz file')
    parser.add_argument('input_files', type=str)
    parser.add_argument('lower_limit', type=float)
    parser.add_argument('upper_limit', type=float)
    parser.add_argument('output_id', type=int)
    parser.add_argument('-mode', '--p_type', type=str, default='mu-')   #either 'mu-' or 'e-'
    parser.add_argument('-out', '--outputdir', type=str)
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

    if config.outputdir is not None:
        output_dir = config.outputdir + "/"
    else: 
        work_dir = "/gpfs/scratch/mojia/HEPML/TrainingSampleWCSim/"
        output_dir = work_dir + mode + "/" + str(E_lowlimit) + "_" + str(E_uplimit) + "/" 
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    outfile = os.path.join(output_dir, 'wcsimoutput_'+ str(config.output_id)+'.npz')
    print(outfile)

    rd = wcsim_reader.Reader()
    print("Initialized reader")

    rd.addFile(config.input_files)

    mask_top = rd.mask[0].astype(np.float32)
    mask_bottom = rd.mask[2].astype(np.float32)

    top = np.zeros(rd.mask[0].shape)
    barrel = np.zeros(rd.mask[1].shape)
    bottom = np.zeros(rd.mask[2].shape)

    print('TOTAL EVENTS Loaded: ', len(rd))

    print(rd.pmts())
    print('PMTs has been mapped.')

    print("Counting events...")
    events_num = 0
    for evt in rd:
        primary= [p for p in evt[0]["trueTracks"] if p["parenttype"]==0 and p["id"]==1 and p["E"] < E_uplimit and p["E"] > E_lowlimit ]
        events_num += len(primary)
    print("Num of Events:", events_num, " with energy < ", E_uplimit )

    directions = np.empty((events_num, 1, 3), dtype=np.float32)
    energies = np.empty((events_num, 1), dtype=np.float32)
    labels = np.empty((events_num,),dtype=np.float32)
    pids= np.empty((events_num, 1),dtype=np.float32)
    positions= np.empty((events_num, 1, 3),dtype=np.float32)
    event_data= np.empty((events_num, barrel.shape[0], barrel.shape[1], 2), dtype =np.float32)
    event_data_top = np.empty((events_num, top.shape[0], top.shape[1], 2), dtype = np.float32)
    event_data_bottom = np.empty((events_num, bottom.shape[0], bottom.shape[1], 2),dtype = np.float32)

    i = 0
    for iev, event in enumerate(rd) :
        print("EVENT {0}".format(iev))

        for isub, sub in enumerate(event) :
            print ("SUB-EVENT {0}".format(isub))
            particles = [t for t in sub["trueTracks"] if t["parenttype"]==0 and t["id"] == 1]
            if len(particles) == 1:
                evt_energy = particles[0]["E"]
                evt_pid = particles[0]["PDG_code"]
                direction = [particles[0]["dirx"], particles[0]["diry"], particles[0]["dirz"]]
                evt_direction = np.array(direction).reshape(1,3)
            if evt_energy < E_uplimit:
                vertex = sub["vertex"].copy()
                vertex = vertex.view('<f4').reshape(1,3)
                thisTop_q = np.copy(top).astype(float)
                thisTop_t = np.copy(top).astype(float)
 
                thisBarrel_q = np.copy(barrel).astype(float)
                thisBarrel_t = np.copy(barrel).astype(float)

                thisBottom_q = np.copy(bottom).astype(float)
                thisBottom_t = np.copy(bottom).astype(float)
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

            break # end of subevent loop

        if evt_energy >= E_uplimit :
            print("Skip EVENT {0}".format(iev))
            continue
        elif evt_energy <= E_lowlimit :
            print("Skip EVENT {0}".format(iev))
            continue
        else :
            print("Record EVENT {0}".format(iev))
            positions[i] = vertex
            energies[i]= evt_energy
            pids[i]= evt_pid
            directions[i] = evt_direction
            event_data[i,:,:,0] = thisBarrel_q
            event_data[i,:,:,1] = thisBarrel_t
            event_data_top[i,:,:,0] = thisTop_q
            event_data_top[i,:,:,1] = thisTop_t
            event_data_bottom[i,:,:,0] = thisBottom_q
            event_data_bottom[i,:,:,1] = thisBottom_t
            labels[i] = pid_label # primitive setting
            i += 1
            del thisTop_q, thisTop_t, thisBarrel_q, thisBarrel_t, thisBottom_q, thisBottom_t

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
    
    print("Num of Events:", events_num, " with energy < ", E_uplimit )
    print("Saved", i, " events.")

