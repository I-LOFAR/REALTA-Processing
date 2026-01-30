'''
Code Purpose: Search voltage in a given directory and find corresponding .fil files, check sizes and remove. 
Author: Owen A. Johnson
'''

import pandas as pd 
import datetime 
import numpy as np
from glob import glob
import os 

def grab_time(logfile):
    with open(logfile, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        if 'running for max' in line:
            parts = line.split()
            time_sec = float(parts[3])
            return time_sec
    
    return None 

def expected_size(nbit, obs_time, nchan=3904, tsamp=0.00065536):
    
            nsamps = obs_time / tsamp
            nbytes = nbit / 8

            size_bytes = nchan * nsamps * nbytes
            return size_bytes / (1024**3)

def main():

    volt_df = pd.read_csv('./csv_files/REALTA-Voltage-Files.csv')
    fil_df = pd.read_csv('./csv_files/REALTA-Observation-Files.csv')
    sched_df = pd.read_csv('./csv_files/REALTA-Sched-Metadata.csv')

    fil_mjd = fil_df['time_mjd'].dropna()
    fil_mjd = np.array(fil_mjd.tolist())
    fil_mjd = np.where(fil_mjd == 'hdr error', 10, fil_mjd)
    fil_mjd = fil_mjd.astype(float)
    
    sched_strtdates = sched_df['start'] #format YYYY-MM-DDTHH:MM

    # for each voltage mjd see if there is a filterbank within 10 (1e-4) seconds
    matches = []
    for index, row in volt_df.iterrows():
        v_mjd = row['MJD']
        diffs = np.abs(fil_mjd - v_mjd)
        close_idxs = np.where(diffs < 0.000127315)[0]

        if len(close_idxs) > 0:
            for idx in close_idxs:
                fil_details = fil_df.iloc[idx]
                volt_path = row['Path']
                print(f"\nVoltage File Path: {volt_path}")
                print(f"Voltage Size (GB): {row['Total Size (GB)']}")
                print(f"Lane Count: {row['Lane Count']}")
                print(f"Voltage Date: {row['Date']}")
                
                fil_path = fil_details['filename']
                fil_gb = fil_details['size_gb']
                fil_tobs = float(fil_details['tobs_min'])
                fil_utc = fil_details['time_utc'] #format YYYY-MM-DDTHH:MM:SS
                
            
                print(f"\nCorresponding .fil file: {fil_path}")
                print(f"Observation Time (min): {fil_tobs}")
                print(f"Size (GB): {fil_gb}")
                print(f"Expected 8-bit Size (GB): {expected_size(8, fil_tobs*60):.2f}")
                print(f"Expected 32-bit Size (GB): {expected_size(32, fil_tobs*60):.2f}")
                
                # find matching schedule entry
                fil_start = fil_utc[:16]  # Truncate to YYYY-MM-DDTHH:MM
                sched_match = sched_strtdates[sched_strtdates.str.startswith(fil_start)]   
                
                if not sched_match.empty:
                    # print row 
                    sched_row = sched_df.iloc[sched_match.index[0]]
                    source = sched_row['source']
                    time = sched_row['start']
                    dur = sched_row['duration_min']
                    print(f"\nMatched Schedule Entry - Source: {source}, Start: {time}, Duration (min): {dur}")
                    
                else:
                    print("\nNo matching schedule entry found.")

                    
                # ask to delete voltages
                user_input = input("\nDo you want to delete the corresponding voltage files? (y/n): ")
                if user_input.lower() == 'y':
                    # remove all .zst files in voltage path 
                    zst_files = glob(os.path.join(volt_path, '*.zst'))
                    for zst_file in zst_files:
                        os.remove(zst_file)
                        print(f"Deleted file: {zst_file}")
                    print("All corresponding voltage files deleted.")   
                else:
                    print("No files were deleted.")
                
                print('-' * 30)
                
            

if __name__ == "__main__":
    main()