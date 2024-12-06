import sys
import os.path as path
import subprocess

def main():
    DATA_DIR=sys.argv[1]
    OUT_DIR=sys.argv[2]
    CP_INTERVAL=sys.argv[3] if len(sys.argv) >= 4 else 0
    TEST_NAMES = sys.argv[4:]

    test_names =  TEST_NAMES
    if TEST_NAMES == []:
        test_names = ['cifar10', 'cifar100', 'cifarN', 'clothing1m', 'webvision']
    
    for fname in test_names:
        subprocess.call(
            path.join('./test', fname),
            DATA_DIR,
            OUT_DIR,
            CP_INTERVAL
        )

if __name__ == '__main__':
    main()