import tarfile
import numpy as np
import pandas as pd
import os
import sys
from six.moves import cPickle

def main():
    # See https://github.com/mila-iqia/fuel/blob/master/fuel/converters/cifar100.py

    SRC_DIR=sys.argv[1]
    DEST_DIR=sys.argv[2]

    input_file = os.path.join(SRC_DIR, 'cifar-10-python.tar.gz')
    tar_file = tarfile.open(input_file, 'r:gz')

    batches = []
    for k in range(1, 6):    
        file = tar_file.extractfile(f'cifar-10-batches-py/data_batch_{k}')
        data = cPickle.load(file, encoding='latin1')

        batches.append(data)
        file.close()

    train = {
        'labels': [],
        'data': []
    }
    for i in range(0, 5):
        train['labels'].extend(list(batches[i]['labels']))
        train['data'].extend(list(batches[i]['data']))

    file = tar_file.extractfile(f'cifar-10-batches-py/test_batch')
    test = cPickle.load(file, encoding='latin1')
    file.close()

    print("Total Dataset Examples Size: ", len(train['data']))
    print("Total Dataset Testing Size: ", len(test['data']))

    def subsample(labels, images):
        # See https://stackoverflow.com/questions/62547807/how-to-create-cifar-10-subset
        df = pd.DataFrame(list(zip(images, labels)), columns =['images', 'labels']) 
        val = df.sample(frac=0.05, random_state=0)
        return ( val, len(val['images']) )

    train_df, train_size = subsample(train['labels'], train['data'])
    test_df, test_size = subsample(test['labels'], test['data'])

    print("Subsampled training: ", train_size)
    print("Subsampled testing: ", test_size)

    train_df.to_pickle(os.path.join(DEST_DIR, 'train_batch'))
    test_df.to_pickle(os.path.join(DEST_DIR, 'test_batch'))
    

if __name__ == '__main__':
    main()
