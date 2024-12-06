import sys
import os.path as path
import subprocess

def main():
    DATA_DIR=sys.argv[1]
    OUT_DIR=sys.argv[2]
    SRC_DIR= path.join(path.abspath(path.dirname(__file__)), '..', 'src')
    CP_INTERVAL=sys.argv[3]

    PATH = path.join(SRC_DIR, 'clothing1m/sgn.py')

    print('############# CLOTHING-1M ################')
    subprocess.call(
        PATH,
        f'--data_dir={DATA_DIR}/clothing1m',
        f'--output_dir={OUT_DIR}/clothing1m',
        f'--checkpoint_interval={CP_INTERVAL}'
    )

if __name__ == '__main__':
    main()