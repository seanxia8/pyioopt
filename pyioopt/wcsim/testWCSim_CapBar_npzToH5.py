import numpy as np
import argparse
import os
import h5py

def get_arg():
    parser = argparse.ArgumentParser(description='convert and merge .npz files to hdf5')
    parser.add_argument('input_dir', type=str)
    parser.add_argument('output_dir', type=str)
    parser.add_argument('-mode', '--p_type', type=str, default='mu-')
    args = parser.parse_args()
    return args

if __name__=='__main__':
    config = get_arg()

    files = []
    for f in os.listdir(config.input_dir):
        if f.endswith(".npz"):
            files.append(os.path.join(config.input_dir, f))
            print(os.path.join(config.input_dir, f))

    total_evts = 0
    for input_file in files:
        npz_file = np.load(input_file)
        eng = npz_file['energies'] 
        total_evts += eng.shape[0]       
    
    print("Found ", total_evts, " events!")

    num_pmt_row = np.load(files[0])['event_data'].shape[1]
    num_pmt_col = np.load(files[0])['event_data'].shape[2] 
    num_pmt_row_top = np.load(files[0])['event_data_top'].shape[1]
    num_pmt_col_top = np.load(files[0])['event_data_top'].shape[2] 
    num_pmt_row_bottom = np.load(files[0])['event_data_bottom'].shape[1]
    num_pmt_col_bottom = np.load(files[0])['event_data_bottom'].shape[2] 

    mask_array_top = np.load(files[0])['mask_top']
    mask_array_bottom = np.load(files[0])['mask_bottom']

    dset_size = total_evts
    output_directory = config.output_dir
    mode = config.p_type
    output_file = output_directory + "WCSim_" + mode + "_npztoh5_test.h5"
#    output_file="/gpfs/scratch/mojia/HEPML/TrainingSampleWCSim/WCSim_mu-_npztoh5_test.h5"

    with h5py.File(output_file,'w') as f:
        f.attrs['CLASS'] = np.array('GROUP', dtype='S')
        f.attrs['TITLE'] = np.array('', dtype='S')
        f.attrs['FILTERS'] = 65797
        f.attrs['PYTABLES_FORMAT_VERSION'] = np.array('2.1', dtype='S') 
        f.attrs['VERSION'] = np.array('1.0', dtype='S')

        dset_directions=f.create_dataset("directions", shape=(dset_size, 1, 3), dtype=np.float32, maxshape=(None, 1, 3),chunks=(1, 1, 3), compression="gzip", compression_opts=5, shuffle=True)
        dset_energies=f.create_dataset("energies", shape=(dset_size, 1), dtype=np.float32, maxshape=(None, 1), chunks=(1, 1), compression="gzip", compression_opts=5, shuffle=True)
        dset_labels=f.create_dataset("labels", shape=(dset_size, ), dtype=np.float32 , chunks=True, compression="gzip", compression_opts=5, shuffle=True)
        dset_pids=f.create_dataset("pids", shape=(dset_size, 1), dtype=np.float32, maxshape=(None, 1), chunks=(1, 1), compression="gzip", compression_opts=5, shuffle=True)
        dset_positions=f.create_dataset("positions", shape=(dset_size, 1, 3), dtype=np.float32, maxshape=(None, 1, 3), chunks=(1, 1, 3), compression="gzip", compression_opts=5, shuffle=True)
        dset_event_data=f.create_dataset("event_data", shape=(dset_size, num_pmt_row, num_pmt_col, 2), dtype=np.float32, 
                                         maxshape=(None, num_pmt_row, num_pmt_col, 2), chunks=(1, num_pmt_row, num_pmt_col, 2), 
                                         compression="gzip", compression_opts=5, shuffle=True)
        dset_event_data_top=f.create_dataset("event_data_top", shape=(dset_size, num_pmt_row_top, num_pmt_col_top, 2), dtype=np.float32, 
                                         maxshape=(None, num_pmt_row_top, num_pmt_col_top, 2), chunks=(1, num_pmt_row_top, num_pmt_col_top, 2), 
                                         compression="gzip", compression_opts=5, shuffle=True)
        dset_event_data_bottom=f.create_dataset("event_data_bottom", shape=(dset_size, num_pmt_row_bottom, num_pmt_col_bottom, 2), dtype=np.float32, 
                                         maxshape=(None, num_pmt_row_bottom, num_pmt_col_bottom, 2), chunks=(1, num_pmt_row_bottom, num_pmt_col_bottom, 2), 
                                         compression="gzip", compression_opts=5, shuffle=True)
        dset_mask = f.create_dataset("mask", shape=(2, num_pmt_row_top, num_pmt_col_top), dtype=np.float32, chunks=(1,num_pmt_row_top,num_pmt_col_top), compression="gzip", compression_opts=5, shuffle=True)

        for dataset in [dset_directions, dset_energies, dset_pids, dset_positions, dset_event_data, dset_event_data_top, dset_event_data_bottom]:
            dataset.attrs['CLASS']=np.array('EARRAY',dtype='S')
            dataset.attrs['TITLE']=np.array('',dtype='S')
            dataset.attrs['VERSION']=np.array('1.1', dtype='S')
            dataset.attrs['EXTDIM'] =np.int32(0)

        dset_labels.attrs['CLASS'] = np.array('CARRAY',dtype = 'S')
        dset_labels.attrs['TITLE'] = np.array('',dtype='S')
        dset_labels.attrs['VERSION']=np.array('1.1', dtype='S')

        dset_mask[0] = mask_array_top
        dset_mask[1] = mask_array_bottom

        offset = 0
        offset_next = 0
        for input_file in files:
            print(input_file)
            input_arr = np.load(input_file)
            offset_next += input_arr['energies'].shape[0]

            dset_energies[offset:offset_next] = input_arr['energies']
            dset_labels[offset:offset_next] = input_arr['labels']
            dset_pids[offset:offset_next] = input_arr['pids']
            dset_directions[offset:offset_next] = input_arr['directions']
            dset_positions[offset:offset_next] = input_arr['positions']
            dset_event_data[offset:offset_next] = input_arr['event_data']
            dset_event_data_top[offset:offset_next] = input_arr['event_data_top']
            dset_event_data_bottom[offset:offset_next] = input_arr['event_data_bottom']

            offset = offset_next

#print("Num of Events:", events_num, " with energy < ", E_uplimit )
    print("Saved", offset, " events.")

