import sys
import os.path as path
import subprocess

def main():
    DATA_DIR=sys.argv[1]
    OUT_DIR=sys.argv[2]
    SRC_DIR= path.join(path.abspath(path.dirname(__file__)), '..', 'src')
    CP_INTERVAL=sys.argv[3]

    PATH = path.join(SRC_DIR, 'cifar/sgn.py')

    print('############# CIFAR-N TESTS ################')
    
    print('============= 10N AGGREGATE ==============')

    subprocess.call(
        PATH,
        f'--data_dir={DATA_DIR}/cifarN',
        f'--output_dir={OUT_DIR}/cifarN/aggre',
        '--dataset cifar10_label_corrupted',
        '--noisy_labels',
        '--corruption_type aggre',
        f'--checkpoint_interval={CP_INTERVAL}'
    )

    print('============= 10N RANDOM 1 ==============')

    subprocess.call(
        PATH,
        f'--data_dir={DATA_DIR}/cifarN',
        f'--output_dir={OUT_DIR}/cifarN/rand1',
        '--dataset cifar10_label_corrupted',
        '--noisy_labels',
        '--corruption_type rand1',
        f'--checkpoint_interval={CP_INTERVAL}'
    )

    print('============= 10N RANDOM 2 ==============')

    subprocess.call(
        PATH,
        f'--data_dir={DATA_DIR}/cifarN',
        f'--output_dir={OUT_DIR}/cifarN/rand2',
        '--dataset cifar10_label_corrupted',
        '--noisy_labels',
        '--corruption_type rand2',
        f'--checkpoint_interval={CP_INTERVAL}'
    )

    print('============= 10N RANDOM 3 ==============')
    
    subprocess.call(
        PATH,
        f'--data_dir={DATA_DIR}/cifarN',
        f'--output_dir={OUT_DIR}/cifarN/rand3',
        '--dataset cifar10_label_corrupted',
        '--noisy_labels',
        '--corruption_type rand3',
        f'--checkpoint_interval={CP_INTERVAL}'
    )

    print('============= 10N WORST ==============')
    
    subprocess.call(
        PATH,
        f'--data_dir={DATA_DIR}/cifarN',
        f'--output_dir={OUT_DIR}/cifarN/worst',
        '--dataset cifar10_label_corrupted',
        '--noisy_labels',
        '--corruption_type worst',
        f'--checkpoint_interval={CP_INTERVAL}'
    )

    print('============= CIFAR-100N ==============')
    
    subprocess.call(
        PATH,
        f'--data_dir={DATA_DIR}/cifarN',
        f'--output_dir={OUT_DIR}/cifarN/c100n',
        '--dataset cifar10_label_corrupted',
        '--noisy_labels',
        '--corruption_type c100noise',
        f'--checkpoint_interval={CP_INTERVAL}'
    )

if __name__ == '__main__':
    main()