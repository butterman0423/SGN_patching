"""cifar10 dataset."""

import tensorflow_datasets as tfds
import pandas as pd
from six.moves import cPickle

_CITATION = """\
@TECHREPORT{Krizhevsky09learningmultiple,
    author = {Alex Krizhevsky},
    title = {Learning multiple layers of features from tiny images},
    institution = {},
    year = {2009}
}
"""

class Builder(tfds.core.GeneratorBasedBuilder):
  """DatasetBuilder for cifar10 dataset."""

  VERSION = tfds.core.Version('1.0.0')
  RELEASE_NOTES = {
      '1.0.0': 'Initial release.',
  }

  MANUAL_DOWNLOAD_INSTRUCTIONS = """
  Run SGN_patching/subsample/subsample-cifar10.py first and place the resulting
  archive in <path/to/manual_dir>.
  Specify location with --manual_dir=<path>
  """

  def _info(self) -> tfds.core.DatasetInfo:
    """Returns the dataset metadata."""
    return self.dataset_info_from_configs(
        description=(
            "A subsample of the CIFAR-10 dataset. "
            "This is a 5% subsample containing 2500 training images, 500 test images"
        ),
        features=tfds.features.FeaturesDict({
            'id': tfds.features.Text(),
            'image': tfds.features.Image(shape=(32, 32, 3)),
            'label': tfds.features.ClassLabel(num_classes=10),
        }),
        supervised_keys=('image', 'label'), 
        homepage='https://www.cs.toronto.edu/~kriz/cifar.html',
        citation=_CITATION
    )

  def _split_generators(self, dl_manager: tfds.download.DownloadManager):

    """Returns SplitGenerators."""
    archive_path = dl_manager.manual_dir / 'cifar10.tar'
    extracted_path = dl_manager.extract(archive_path)

    return {
        tfds.Split.TRAIN: self._generate_examples(extracted_path / 'train_batch', 'train'),
        tfds.Split.TEST: self._generate_examples(extracted_path / 'test_batch', 'test')
    }

  def _generate_examples(self, path, ex_type):
    file = open(path, "rb")
    ds = cPickle.load(file, encoding='latin1')
    index = 0  # Using index as key since data is always loaded in same order.

    ds_images = ds['images']
    ds_labels = ds['labels']

    for img, label in zip(ds_images, ds_labels):
        record = dict()

        record["id"] = f'{ex_type}_{index}'
        record["label"] = label
        record["image"] = (
                img.reshape((3, 32, 32))
                .transpose((1, 2, 0))
        )

        yield index, record
        index += 1
    file.close()
