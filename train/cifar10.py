import sys
import os.path as path
import subprocess

def main():
    DATA_DIR=sys.argv[1]
    OUT_DIR=sys.argv[2]
    SRC_DIR= path.join(path.abspath(path.dirname(__file__)), '..', 'src')
    CP_INTERVAL=sys.argv[3]

    PATH = path.join(SRC_DIR, 'cifar/sgn.py')

    print('############# CIFAR-10 TESTS ################')
    
    print('============= NO NOISE ==============')
    subprocess.call(
        PATH,
        f'--data_dir={DATA_DIR}/cifar10',
        f'--output_dir={OUT_DIR}/cifar10/no_noise',
        '--dataset cifar10',
        f'--checkpoint_interval={CP_INTERVAL}'
    )

    print('============= SYM 20 ==============')
    subprocess.call(
        PATH,
        f'--data_dir={DATA_DIR}/cifar10',
        f'--output_dir={OUT_DIR}/cifar10/sym20',
        '--dataset cifar10',
        '--noisy_labels',
        '--corruption_type sym',
        '--severity 0.2',
        f'--checkpoint_interval={CP_INTERVAL}'
    )

    print('============= SYM 40 ==============')
    subprocess.call(
        PATH,
        f'--data_dir={DATA_DIR}/cifar10',
        f'--output_dir={OUT_DIR}/cifar10/sym40',
        '--dataset cifar10',
        '--noisy_labels',
        '--corruption_type sym',
        '--severity 0.4',
        f'--checkpoint_interval={CP_INTERVAL}'
    )

    print('============= SYM 60 ==============')
    subprocess.call(
        PATH,
        f'--data_dir={DATA_DIR}/cifar10',
        f'--output_dir={OUT_DIR}/cifar10/sym60',
        '--dataset cifar10',
        '--noisy_labels',
        '--corruption_type sym',
        '--severity 0.6',
        f'--checkpoint_interval={CP_INTERVAL}'
    )

    print('============= ASYM 20 ==============')
    subprocess.call(
        PATH,
        f'--data_dir={DATA_DIR}/cifar10',
        f'--output_dir={OUT_DIR}/cifar10/asym20',
        '--dataset cifar10',
        '--noisy_labels',
        '--corruption_type asym',
        '--severity 0.2',
        f'--checkpoint_interval={CP_INTERVAL}'
    )

    print('============= ASYM 40 ==============')
    subprocess.call(
        PATH,
        f'--data_dir={DATA_DIR}/cifar10',
        f'--output_dir={OUT_DIR}/cifar10/asym40',
        '--dataset cifar10',
        '--noisy_labels',
        '--corruption_type asym',
        '--severity 0.4',
        f'--checkpoint_interval={CP_INTERVAL}'
    )

    print('============= ASYM 60 ==============')
    subprocess.call(
        PATH,
        f'--data_dir={DATA_DIR}/cifar10',
        f'--output_dir={OUT_DIR}/cifar10/asym60',
        '--dataset cifar10',
        '--noisy_labels',
        '--corruption_type asym',
        '--severity 0.6',
        f'--checkpoint_interval={CP_INTERVAL}'
    )

if __name__ == '__main__':
    pass