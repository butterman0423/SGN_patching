import sys
import os.path as path
import subprocess

def main():
    DATA_DIR=sys.argv[1]
    OUT_DIR=sys.argv[2]
    SRC_DIR= path.join(path.abspath(path.dirname(__file__)), '..', 'src')
    CP_INTERVAL=sys.argv[3]
    
    PATH = path.join(SRC_DIR, 'webvision/sgn.py')
    
    print('############# WEBVISION ################')

    subprocess.call(
        PATH,
        f'--data_dir: {DATA_DIR}/webvision',
        f'--output_dir: {OUT_DIR}/webvision',
        f'--checkpoint_interval: {CP_INTERVAL}'
    )