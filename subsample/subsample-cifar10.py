import tarfile
import numpy as np
import pandas as pd
import os
from six.moves import cPickle

def main():
    # See https://github.com/mila-iqia/fuel/blob/master/fuel/converters/cifar100.py

    input_file = os.path.join("datasets/raw", 'cifar-10-python.tar.gz')
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

        #creating the validation set from the training set
        df = pd.DataFrame(list(zip(images, labels)), columns =['image', 'labels']) 
        val = df.sample(frac=0.05)
        X_train = np.array([ i for i in list(val['image'])])
        y_train = np.array([ i for i in list(val['labels'])])

        return ( X_train, y_train, val )

    train_feat, train_labels, train_df = subsample(train['labels'], train['data'])
    test_feat, test_labels, test_df = subsample(test['labels'], test['data'])

    print("Subsampled training: ", len(train_feat))
    print("Subsampled testing: ", len(test_feat))

    train_df.to_pickle("datasets/subsample/cifar10/data")
    test_df.to_pickle("datasets/subsample/cifar10/train")
    

if __name__ == '__main__':
    main()