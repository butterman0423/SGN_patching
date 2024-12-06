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
        df = pd.DataFrame(list(zip(images, f_labels, c_labels)), columns =['image', 'fine_labels', 'coarse_labels']) 
        val = df.sample(frac=0.05, random_state=0)
        X_train = np.array([ i for i in list(val['image'])])
        y_train = np.array([ i for i in list(val['fine_labels'])])

        return ( X_train, y_train, val )

    train_feat, train_labels, train_df = subsample(train['fine_labels'], train['coarse_labels'], train['data'])
    test_feat, test_labels, test_df = subsample(test['fine_labels'], test['coarse_labels'], test['data'])

    print("Subsampled training: ", len(train_feat))
    print("Subsampled testing: ", len(test_feat))

    train_df.to_pickle("datasets/subsample/cifar100/data")
    test_df.to_pickle("datasets/subsample/cifar100/train")
    

if __name__ == '__main__':
    main()