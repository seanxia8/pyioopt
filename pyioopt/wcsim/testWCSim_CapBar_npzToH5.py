import numpy as np
import argparse
import os
import h5py
import re
import itertools

def get_arg():
    parser = argparse.ArgumentParser(description='convert and merge .npz files to hdf5')
    parser.add_argument('-i',     '--input_dir',   type=str)
    parser.add_argument('-o',     '--output_dir',  type=str)
    parser.add_argument('-l',     '--lower_limit', type=float,    default=None)
    parser.add_argument('-u',     '--upper_limit', type=float,    default=None)
    parser.add_argument('-mode',  '--p_type',      type=str,      default='mu-')
    parser.add_argument('-v',     '--veto_unhit',  type=np.bool_, default=False)
    args = parser.parse_args()
    return args

if __name__=='__main__':
    config = get_arg()
    mode = config.p_type
    E_uplimit = config.upper_limit
    E_lowlimit = config.lower_limit

    files = []
    for f in os.listdir(config.input_dir):
        matchPID = re.search(mode, f)
        if f.endswith(".npz") and matchPID:
            files.append(os.path.join(config.input_dir, f))
            print(os.path.join(config.input_dir, f))

    total_evts = 0
    for input_file in files:
        npz_file = np.load(input_file)
        eng = npz_file['energies'] 
        total_evts += eng.shape[0]       
    
    print("Found ", total_evts, " events!")

    num_pmt_barrel = np.load(files[0])['event_data'].shape[1]
    num_pmt_top = np.load(files[0])['event_data_top'].shape[1]
    num_pmt_bottom = np.load(files[0])['event_data_bottom'].shape[1]

    mask_array_top = np.load(files[0])['mask_top']
    mask_array_bottom = np.load(files[0])['mask_bottom']

    #dset_size = total_evts

    if config.output_dir is not None:
        if not os.path.exists(config.output_dir):
            os.mkdir(config.output_dir)
        if not os.path.isdir(config.output_dir):
            raise argparse.ArgumentTypeError("Cannot access or create output directory" + config.outputdir)
        output_dir = config.output_dir
        output_file = os.path.join(output_dir, "wcsimoutput_" + mode + "_" + str(E_lowlimit) + "_" + str(E_uplimit) + "_hitonly_" + str(config.veto_unhit) + ".h5")
    else:
        print("Output dir not specified, save the outputs in the same dir as input files.")
        output_file = os.path.splitext(infiles)[0] + "_hitonly_" + str(config.veto_unhit) + ".h5"

    print("Output file is: ", output_file)

    #temp_data_barrel = []
    #temp_data_top = []
    #temp_data_bottom = []

    with h5py.File(output_file,'w') as f:
        f.attrs['CLASS'] = np.array('GROUP', dtype='S')
        f.attrs['TITLE'] = np.array('', dtype='S')
        f.attrs['FILTERS'] = 65797
        f.attrs['PYTABLES_FORMAT_VERSION'] = np.array('2.1', dtype='S') 
        f.attrs['VERSION'] = np.array('1.0', dtype='S')

        dset_directions=f.create_dataset("directions", shape=(total_evts, 1, 3), dtype=np.float32, maxshape=(total_evts, 1, 3), compression="gzip", compression_opts=5, shuffle=True)
        dset_energies=f.create_dataset("energies", shape=(total_evts, 1), dtype=np.float32, maxshape=(total_evts, 1), compression="gzip", compression_opts=5, shuffle=True)
        dset_labels=f.create_dataset("labels", shape=(total_evts, 1), dtype=np.float32, maxshape=(total_evts, 1), compression="gzip", compression_opts=5, shuffle=True)
        dset_pids=f.create_dataset("pids", shape=(total_evts, 1), dtype=np.float32, maxshape=(total_evts, 1), compression="gzip", compression_opts=5, shuffle=True)
        dset_positions=f.create_dataset("positions", shape=(total_evts, 1, 3), dtype=np.float32, maxshape=(total_evts, 1, 3), compression="gzip", compression_opts=5, shuffle=True)

        dset_event_data=f.create_dataset("event_data_barrel", shape=(total_evts*num_pmt_barrel, 3), dtype=np.float32, maxshape=(total_evts*num_pmt_barrel, 3), compression="gzip", compression_opts=5, shuffle=True)
        dset_event_data_top=f.create_dataset("event_data_top", shape=(total_evts*num_pmt_top, 3), dtype=np.float32, maxshape=(total_evts*num_pmt_top, 3), compression="gzip", compression_opts=5, shuffle=True)
        dset_event_data_bottom=f.create_dataset("event_data_bottom", shape=(total_evts*num_pmt_bottom, 3), dtype=np.float32, maxshape=(total_evts*num_pmt_bottom, 3),  compression="gzip", compression_opts=5, shuffle=True)


        dset_hit_index=f.create_dataset("hit_index_barrel", shape=(total_evts, 1), dtype=np.int32, 
                                        maxshape=(total_evts, 1), 
                                        compression="gzip", compression_opts=5, shuffle=True)

        dset_hit_index_top=f.create_dataset("hit_index_top", shape=(total_evts, 1), dtype=np.int32, 
                                            maxshape=(total_evts, 1), 
                                            compression="gzip", compression_opts=5, shuffle=True)
        dset_hit_index_bottom=f.create_dataset("hit_index_bottom", shape=(total_evts, 1), dtype=np.int32, 
                                               maxshape=(total_evts, 1), 
                                               compression="gzip", compression_opts=5, shuffle=True)

        dset_nhit=f.create_dataset("nhit_barrel", shape=(total_evts, 1), dtype=np.int32, 
                                   maxshape=(total_evts, 1), 
                                   compression="gzip", compression_opts=5, shuffle=True)
        dset_nhit_top=f.create_dataset("nhit_top", shape=(total_evts, 1), dtype=np.int32, 
                                       maxshape=(total_evts, 1), 
                                       compression="gzip", compression_opts=5, shuffle=True)
        dset_nhit_bottom=f.create_dataset("nhit_bottom", shape=(total_evts, 1), dtype=np.int32, 
                                          maxshape=(total_evts, 1), 
                                          compression="gzip", compression_opts=5, shuffle=True)
        
        dset_mask = f.create_dataset("mask", shape=(2, num_pmt_top), dtype=np.bool_, maxshape=(2, num_pmt_top), chunks=(1,num_pmt_top), compression="gzip", compression_opts=5, shuffle=True)

        for dataset in [dset_directions, dset_energies, dset_pids, dset_positions, dset_event_data, dset_event_data_top, dset_event_data_bottom, dset_hit_index, dset_hit_index_top, dset_hit_index_bottom, dset_nhit, dset_nhit_top, dset_nhit_bottom]:
            dataset.attrs['CLASS']=np.array('EARRAY',dtype='S')
            dataset.attrs['TITLE']=np.array('',dtype='S')
            dataset.attrs['VERSION']=np.array('1.1', dtype='S')
            dataset.attrs['EXTDIM'] =np.int32(0)

        dset_labels.attrs['CLASS'] = np.array('CARRAY',dtype = 'S')
        dset_labels.attrs['TITLE'] = np.array('',dtype='S')
        dset_labels.attrs['VERSION']=np.array('1.1', dtype='S')

        dset_mask[0] = np.array(mask_array_top, dtype=bool)
        dset_mask[1] = np.array(mask_array_bottom, dtype=bool)

        offset = 0
        offset_next = 0

        barrel_hit_offset = 0
        barrel_hit_offset_next = 0
        top_hit_offset = 0
        top_hit_offset_next = 0
        bottom_hit_offset = 0
        bottom_hit_offset_next = 0

        for input_file in files:
            #print(input_file)
            input_arr = np.load(input_file)
            offset_next += input_arr['energies'].shape[0]

            dset_energies[offset:offset_next] = input_arr['energies']
            dset_labels[offset:offset_next] = input_arr['labels']
            dset_pids[offset:offset_next] = input_arr['pids']
            dset_directions[offset:offset_next] = input_arr['directions']
            dset_positions[offset:offset_next] = input_arr['positions']
            
                
            if config.veto_unhit:

                for i, (event_barrel, event_top, event_bottom) in enumerate(zip(input_arr['event_data'], input_arr['event_data_top'], input_arr['event_data_bottom'])):      
                    hit_indices_barrel = np.where(event_barrel[:,0]>0)
                    hit_indices_top = np.where(event_top[:,0]>0)
                    hit_indices_bottom = np.where(event_bottom[:,0]>0) 

                    dset_nhit[offset+i] = len(hit_indices_barrel[0])
                    dset_nhit_top[offset+i] = len(hit_indices_top[0])
                    dset_nhit_bottom[offset+i] = len(hit_indices_bottom[0])                

                    dset_hit_index[offset+i] = barrel_hit_offset
                    dset_hit_index_top[offset+i] = top_hit_offset
                    dset_hit_index_bottom[offset+i] = bottom_hit_offset
                    
                    barrel_hit_offset_next += len(hit_indices_barrel[0])
                    top_hit_offset_next += len(hit_indices_top[0])
                    bottom_hit_offset_next += len(hit_indices_bottom[0])
                
                    dset_event_data[barrel_hit_offset:barrel_hit_offset_next] = event_barrel[hit_indices_barrel]
                    dset_event_data_top[top_hit_offset:top_hit_offset_next] = event_top[hit_indices_top]
                    dset_event_data_bottom[bottom_hit_offset:bottom_hit_offset_next] = event_bottom[hit_indices_bottom]

                    barrel_hit_offset = barrel_hit_offset_next
                    top_hit_offset = top_hit_offset_next
                    bottom_hit_offset = bottom_hit_offset_next

                #print(max_hit_barrel, max_hit_top, max_hit_bottom)
                #print(len(temp_data_barrel), temp_data_barrel[0].shape, temp_data_barrel[1].shape)
                #temp_data_barrel_trunc = np.column_stack((itertools.zip_longest(*temp_data_barrel[:,:,0], fillvalue=0)))
                #print(temp_data_barrel, temp_data_barrel_trunc)

                #dset_event_data[offset:offset_next] = input_arr['event_data'].reshape(offset_next-offset, -1, input_arr['event_data'].shape[-1])
                #dset_event_data_top[offset:offset_next] = input_arr['event_data_top'].reshape(offset_next-offset, -1, input_arr['event_data_top'].shape[-1])
                #dset_event_data_bottom[offset:offset_next] = input_arr['event_data_bottom'].reshape(offset_next-offset, -1, input_arr['event_data_bottom'].shape[-1])
                
                    
            else:
                dset_event_data[offset:offset_next] = input_arr['event_data'].reshape(1, input_arr['event_data'].shape[-1])
                dset_event_data_top[offset:offset_next] = input_arr['event_data_top'].reshape(1, input_arr['event_data_top'].shape[-1])
                dset_event_data_bottom[offset:offset_next] = input_arr['event_data_bottom'].reshape(1, input_arr['event_data_bottom'].shape[-1])
                
                dset_nhit[offset:offset_next] = np.full((total_evts, 1), num_pmt_barrel, dtype=np.int32)
                dset_nhit_top[offset:offset_next] = np.full((total_evts, 1), num_pmt_top, dtype=np.int32)
                dset_nhit_bottom[offset:offset_next] = np.full((total_evts, 1), num_pmt_bottom, dtype=np.int32)
                
                dset_hit_index[offset:offset_next] = (np.indices((total_evts,), dtype=np.int32)*num_pmt_barrel).reshape((total_evts,1))
                dset_hit_index_top[offset:offset_next] = (np.indices((total_evts,), dtype=np.int32)*num_pmt_top).reshape((total_evts,1))
                dset_hit_index_bottom[offset:offset_next] = (np.indices((total_evts,), dtype=np.int32)*num_pmt_bottom).reshape((total_evts, 1))

                                
            offset = offset_next

        if config.veto_unhit:
            dset_event_data.resize((barrel_hit_offset_next, dset_event_data.shape[1]))
            dset_event_data_top.resize((top_hit_offset_next, dset_event_data_top.shape[1]))
            dset_event_data_bottom.resize((bottom_hit_offset_next, dset_event_data_bottom.shape[1]))

        print(dset_event_data.shape, dset_nhit.shape)
        print(dset_labels.shape)

    #print("Num of Events:", events_num, " with energy < ", E_uplimit )
    print("Saved", offset, " events.")

