import os 
import pandas as pd 
from datetime import datetime


def main():
    volt_df = pd.read_csv('./file-list/REALTA-Voltage-Files.csv')
    print(volt_df.keys())
    volt_df = volt_df[volt_df['Header Path'] != 'Unknown']
    
    docker = (
    "docker run -it --gpus all --rm --network=host "
    "--env DISPLAY=$DISPLAY "
    "--volume=$HOME/.Xauthority:/hosthome/.Xauthority:rw "
    "-v /tmp/.X11-unix:/tmp/.X11-unix "
    "-v /mnt:/mnt "
    "-w $(pwd) "
    "clfd-psrchive-python3.6"
    )


    
    for index, row in volt_df.iterrows():
        target = row['Target']
        date = row['Date']
        path = row['Path']
        extra_suffix = target + '_' + date.replace(' ', '_').replace(':', '-')
        
        # execute cdmtProc.py in dckrgpu environment
        cmd = (
            f'python ./cdmtProc.py -i {path} -o ./cdmtSH --extra {extra_suffix}'
        )

        os.system(cmd)
    
if __name__ == "__main__":
    main()