'''
Code Purpose: Find filterbanks in a given directory and sort them into a master directory based on date and source name. 
'''

import your
import os 
import glob 
import argparse 

def get_args():
    parser = argparse.ArgumentParser(description="Find filterbanks in a given directory and sort them into a master directory based on date and source name.")
    parser.add_argument('-i', '--input_dir', type=str, required=True, help='Input directory to search for filterbank files.')
    parser.add_argument('-o', '--output_dir', type=str, required=True, help='Output master directory to sort filterbank files into.')
    return parser.parse_args()

def get_hdr(fil_path):
    hdr = your.Your(fil_path).your_header
    # print(hdr)
    trgt = hdr.source_name
    strt_date = hdr.tstart_utc

    return trgt, strt_date

def main():
    args = get_args()
    input_dir = args.input_dir
    output_dir = args.output_dir

    fil_files = glob.glob(os.path.join(input_dir, '**', '*.fil'), recursive=True)

    print('Number of .fil files found:', len(fil_files))

    for fil in fil_files:
        try:
            trgt, strt_date = get_hdr(fil)
        except Exception as e:
            print(f"Error reading header for {fil}: {e}")
            continue

        date_str = strt_date.split('T')[0]
        target_dir = os.path.join(output_dir, trgt, date_str)
        # print(f"Creating directory: {target_dir}")

        os.makedirs(target_dir, exist_ok=True)

        dest_path = os.path.join(target_dir, os.path.basename(fil))
        os.rename(fil, dest_path)
        # print(f"Moved {fil} to {dest_path}")

if __name__ == "__main__":
    main()