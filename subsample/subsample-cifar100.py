import tarfile
import numpy as np
import pandas as pd
import os
from six.moves import cPickle

def main():
    # See https://github.com/mila-iqia/fuel/blob/master/fuel/converters/cifar100.py

    #output_path = os.path.join("datasets/subsample", "cifar-10")
    input_file = os.path.join("datasets/raw", 'cifar-100-python.tar.gz')
    tar_file = tarfile.open(input_file, 'r:gz')

    file = tar_file.extractfile('cifar-100-python/train')
    train = cPickle.load(file, encoding='latin1')
    file.close()
    
    file = tar_file.extractfile('cifar-100-python/test')
    test = cPickle.load(file, encoding='latin1')
    file.close()

    print("Total Dataset Examples Size: ", len(train['data']))
    print("Total Dataset Testing Size: ", len(test['data']))

    def subsample(f_labels, c_labels, images):
        # See https://stackoverflow.com/questions/62547807/how-to-create-cifar-10-subset

        #creating the validation set from the training set
        df = pd.DataFrame(list(zip(images, f_labels, c_labels)), columns =['images', 'fine_labels', 'coarse_labels']) 
        val = df.sample(frac=0.05, random_state=0)
        return ( val, len(val['images']) )

    train_df, train_size = subsample(train['fine_labels'], train['coarse_labels'], train['data'])
    test_df, test_size = subsample(test['fine_labels'], test['coarse_labels'], test['data'])

    print("Subsampled training: ", train_size)
    print("Subsampled testing: ", test_size)

    train_df.to_pickle("datasets/subsample/cifar100/train_batch")
    test_df.to_pickle("datasets/subsample/cifar100/test_batch")
    

if __name__ == '__main__':
    main()
