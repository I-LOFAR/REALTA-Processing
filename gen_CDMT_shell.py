#!/usr/bin/env python
import os 
import pandas as pd 
from datetime import datetime
import argparse 

def get_args():
    parser = argparse.ArgumentParser(description="Generate cdmtProc.sh scripts for voltage files using David's orginial script.")
    parser.add_argument('-i', '--stage', type=str, required=False, default='/mnt/ucc4_data2/data/filterbanks/staging_area', help='Staging Area where filterbanks will be generated!')
    parser.add_argument('-csv', '--csv_file', type=str, required=False, default='/mnt/ucc4_data2/data/Owen/software/REALTA-Processing/csv_files/REALTA-Voltage-Files.csv', help='CSV file containing voltage file metadata.')
    return parser.parse_args()


def main():
    args = get_args()
    stage_area = args.stage
    csv_file = args.csv_file
    cdmtProc_path = '/mnt/ucc4_data2/data/Owen/software/REALTA-Processing/cdmtProc.py'
    
    # os.system("find_voltage.py")
    volt_df = pd.read_csv(csv_file)
    volt_df = volt_df[volt_df['Header Path'] != 'Unknown']

    # Sort by GB 
    volt_df = volt_df.sort_values(by='Total Size (GB)', ascending=False)
    volt_df = volt_df[volt_df['Total Size (GB)'] > 1]  # remove voltage dirs that have 0.0 GB size
    
    i = 1 
    for index, row in volt_df.iterrows():
        target = row['Target']
        date = row['Date']
        path = row['Path']
        extra_suffix = target + '_' + date.replace(' ', '_').replace(':', '-')
        
        # mkdir - {stage_area}/0000-{target}-/{date}-(sizeGB)
        date_str = date.split(' ')[0]
        size_gb = row['Total Size (GB)']
        dir_name = f"{i:04d}-{target}-{date_str}-({size_gb:.2f}GB)"
        full_dir = os.path.join(stage_area, dir_name)
        
        os.makedirs(full_dir, exist_ok=True) 
        os.chdir(full_dir)
        os.system(f'cp {cdmtProc_path} ./cdmtProc.py')
    
        # execute cdmtProc.py in dckrgpu environment
        cmd = (
            f'python ./cdmtProc.py -i {path} --extra {extra_suffix}'
        )

        os.system(cmd)
        i += 1
    
if __name__ == "__main__":
    main()