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

def main():

    volt_df = pd.read_csv('./file-list/REALTA-Voltage-Files.csv')
    fil_df = pd.read_csv('./file-list/REALTA-Observation-Files.csv')

    fil_mjd = fil_df['time_mjd'].dropna()
    fil_mjd = np.array(fil_mjd.tolist())
    fil_mjd = np.where(fil_mjd == 'hdr error', 10, fil_mjd)
    fil_mjd = fil_mjd.astype(float)

  
    print(fil_mjd)

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
                log_files = glob(volt_path + '/*.log')
                if len(log_files) > 0:
                    log_path = log_files[0]

                    try: 
                        run_time = grab_time(log_path)
                        print(run_time/60)
                        print(fil_details['tobs_min'])
                    
                    except Exception as e:
                        print(f"Error reading log file {log_path}: {e}")
                        continue

                else:
                    print(f"No log file found for voltage file: {volt_path}. Skipping...")
       

if __name__ == "__main__":
    main()