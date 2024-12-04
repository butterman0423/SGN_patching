def main():
    DATA_DIR="./data"
    OUT_DIR="./out"
    SRC_DIR="./src"
    CP_INTERVAL=10

    print('############# CIFAR-10 TESTS ################')

    PATH = f'{SRC_DIR}/cifar/sgn.py'
    
    print('============= NO NOISE ==============')
    exec(open(PATH).read(), {
        '--data_dir': f'{DATA_DIR}/cifar10',
        '--output_dir': f'{OUT_DIR}/cifar10/no_noise',
        '--dataset': 'cifar10',
        '--checkpoint_interval': CP_INTERVAL
    })

    print('============= SYM 20 ==============')
    exec(open(PATH).read(), {
        '--data_dir': f'{DATA_DIR}/cifar10',
        '--output_dir': f'{OUT_DIR}/cifar10/sym20',
        '--dataset': 'cifar10',
        '--noisy_labels ': '',
        '--corruption_type': 'sym',
        '--severity': 0.2,
        '--checkpoint_interval': CP_INTERVAL
    })

    print('============= SYM 40 ==============')
    exec(open(PATH).read(), {
        '--data_dir': f'{DATA_DIR}/cifar10',
        '--output_dir': f'{OUT_DIR}/cifar10/sym40',
        '--dataset': 'cifar10',
        '--noisy_labels ': '',
        '--corruption_type': 'sym',
        '--severity': 0.4,
        '--checkpoint_interval': CP_INTERVAL
    })

    print('============= SYM 60 ==============')
    exec(open(PATH).read(), {
        '--data_dir': f'{DATA_DIR}/cifar10',
        '--output_dir': f'{OUT_DIR}/cifar10/sym60',
        '--dataset': 'cifar10',
        '--noisy_labels ': '',
        '--corruption_type': 'sym',
        '--severity': 0.6,
        '--checkpoint_interval': CP_INTERVAL
    })

    print('============= ASYM 20 ==============')
    exec(open(PATH).read(), {
        '--data_dir': f'{DATA_DIR}/cifar10',
        '--output_dir': f'{OUT_DIR}/cifar10/sym20',
        '--dataset': 'cifar10',
        '--noisy_labels ': '',
        '--corruption_type': 'sym',
        '--severity': 0.2,
        '--checkpoint_interval': CP_INTERVAL
    })

    print('============= ASYM 40 ==============')
    exec(open(PATH).read(), {
        '--data_dir': f'{DATA_DIR}/cifar10',
        '--output_dir': f'{OUT_DIR}/cifar10/sym20',
        '--dataset': 'cifar10',
        '--noisy_labels ': '',
        '--corruption_type': 'sym',
        '--severity': 0.2,
        '--checkpoint_interval': CP_INTERVAL
    })

    print('============= ASYM 60 ==============')
    exec(open(PATH).read(), {
        '--data_dir': f'{DATA_DIR}/cifar10',
        '--output_dir': f'{OUT_DIR}/cifar10/sym20',
        '--dataset': 'cifar10',
        '--noisy_labels ': '',
        '--corruption_type': 'sym',
        '--severity': 0.2,
        '--checkpoint_interval': CP_INTERVAL
    })

    print('############# CIFAR-100 TESTS ################')

    PATH = f'{SRC_DIR}/cifar/sgn.py'
    
    print('============= NO NOISE ==============')
    exec(open(PATH).read(), {
        '--data_dir': f'{DATA_DIR}/cifar100',
        '--output_dir': f'{OUT_DIR}/cifar100/no_noise',
        '--dataset': 'cifar100',
        '--checkpoint_interval': CP_INTERVAL
    })

    print('============= SYM 20 ==============')
    exec(open(PATH).read(), {
        '--data_dir': f'{DATA_DIR}/cifar100',
        '--output_dir': f'{OUT_DIR}/cifar100/sym20',
        '--dataset': 'cifar100',
        '--noisy_labels ': '',
        '--corruption_type': 'sym',
        '--severity': 0.2,
        '--checkpoint_interval': CP_INTERVAL
    })

    print('============= SYM 40 ==============')
    exec(open(PATH).read(), {
        '--data_dir': f'{DATA_DIR}/cifar100',
        '--output_dir': f'{OUT_DIR}/cifar100/sym40',
        '--dataset': 'cifar100',
        '--noisy_labels ': '',
        '--corruption_type': 'sym',
        '--severity': 0.4,
        '--checkpoint_interval': CP_INTERVAL
    })

    print('============= SYM 60 ==============')
    exec(open(PATH).read(), {
        '--data_dir': f'{DATA_DIR}/cifar100',
        '--output_dir': f'{OUT_DIR}/cifar100/sym60',
        '--dataset': 'cifar100',
        '--noisy_labels ': '',
        '--corruption_type': 'sym',
        '--severity': 0.6,
        '--checkpoint_interval': CP_INTERVAL
    })

    print('============= ASYM 20 ==============')
    exec(open(PATH).read(), {
        '--data_dir': f'{DATA_DIR}/cifar100',
        '--output_dir': f'{OUT_DIR}/cifar100/asym20',
        '--dataset': 'cifar100',
        '--noisy_labels ': '',
        '--corruption_type': 'asym',
        '--severity': 0.2,
        '--checkpoint_interval': CP_INTERVAL
    })

    print('============= ASYM 40 ==============')
    exec(open(PATH).read(), {
        '--data_dir': f'{DATA_DIR}/cifar100',
        '--output_dir': f'{OUT_DIR}/cifar100/asym40',
        '--dataset': 'cifar100',
        '--noisy_labels ': '',
        '--corruption_type': 'asym',
        '--severity': 0.4,
        '--checkpoint_interval': CP_INTERVAL
    })

    print('============= ASYM 60 ==============')
    exec(open(PATH).read(), {
        '--data_dir': f'{DATA_DIR}/cifar100',
        '--output_dir': f'{OUT_DIR}/cifar100/asym20',
        '--dataset': 'cifar100',
        '--noisy_labels ': '',
        '--corruption_type': 'asym',
        '--severity': 0.6,
        '--checkpoint_interval': CP_INTERVAL
    })

    print('############# CIFAR-N TESTS ################')

    PATH = f'{SRC_DIR}/cifar/sgn.py'
    
    print('============= 10N AGGREGATE ==============')
    exec(open(PATH).read(), {
        '--data_dir': f'{DATA_DIR}/cifarN',
        '--output_dir': f'{OUT_DIR}/cifarN/aggre',
        '--dataset': 'cifar10_label_corrupted',
        '--checkpoint_interval': CP_INTERVAL
    })

    print('============= 10N RANDOM 1 ==============')
    exec(open(PATH).read(), {
        '--data_dir': f'{DATA_DIR}/cifarN',
        '--output_dir': f'{OUT_DIR}/cifarN/rand1',
        '--dataset': 'cifar10_label_corrupted',
        '--corruption_type': 'rand1',
        '--checkpoint_interval': CP_INTERVAL
    })

    print('============= 10N RANDOM 2 ==============')
    exec(open(PATH).read(), {
        '--data_dir': f'{DATA_DIR}/cifarN',
        '--output_dir': f'{OUT_DIR}/cifarN/rand2',
        '--dataset': 'cifar10_label_corrupted',
        '--corruption_type': 'rand2',
        '--checkpoint_interval': CP_INTERVAL
    })

    print('============= 10N RANDOM 3 ==============')
    exec(open(PATH).read(), {
        '--data_dir': f'{DATA_DIR}/cifarN',
        '--output_dir': f'{OUT_DIR}/cifarN/rand3',
        '--dataset': 'cifar10_label_corrupted',
        '--corruption_type': 'rand3',
        '--checkpoint_interval': CP_INTERVAL
    })

    print('============= 10N WORST ==============')
    exec(open(PATH).read(), {
        '--data_dir': f'{DATA_DIR}/cifarN',
        '--output_dir': f'{OUT_DIR}/cifarN/worst',
        '--dataset': 'cifar10_label_corrupted',
        '--corruption_type': 'rand3',
        '--checkpoint_interval': CP_INTERVAL
    })

    print('============= CIFAR-100N ==============')
    exec(open(PATH).read(), {
        '--data_dir': f'{DATA_DIR}/cifarN',
        '--output_dir': f'{OUT_DIR}/cifarN/c100n',
        '--dataset': 'cifar100',
        '--corruption_type': 'c100noise',
        '--checkpoint_interval': CP_INTERVAL
    })

    print('############# CLOTHING-1M ################')

    PATH = f'{SRC_DIR}/clothing1m/sgn.py'
    exec(open(PATH).read(), {
        '--data_dir': f'{DATA_DIR}/clothing1m',
        '--output_dir': f'{OUT_DIR}/clothing1m',
        '--checkpoint_interval': CP_INTERVAL
    })

    print('############# WEBVISION ################')

    PATH = f'{SRC_DIR}/webvision/sgn.py'
    exec(open(PATH).read(), {
        '--data_dir': f'{DATA_DIR}/webvision',
        '--output_dir': f'{OUT_DIR}/webvision',
        '--checkpoint_interval': CP_INTERVAL
    })
