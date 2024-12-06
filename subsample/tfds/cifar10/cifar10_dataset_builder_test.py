"""cifar10 dataset."""

import tensorflow_datasets as tfds
from . import cifar10_dataset_builder


class Cifar10Test(tfds.testing.DatasetBuilderTestCase):
  """Tests for cifar10 dataset."""
  DATASET_CLASS = cifar10_dataset_builder.Builder
  SPLITS = {
      'train': 10,  # Number of fake train example
      'test': 3,  # Number of fake test example
  }

if __name__ == '__main__':
  tfds.testing.test_main()
