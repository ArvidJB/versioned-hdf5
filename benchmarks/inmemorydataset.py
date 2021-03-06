import os

import h5py
from versioned_hdf5 import VersionedHDF5File
from versioned_hdf5.wrappers import InMemoryDataset

import numpy as np

class TimeInMemoryDataset:
    timeout = 1000

    def setup(self):
        with h5py.File('bench.hdf5', 'w') as f:
            versioned_file = VersionedHDF5File(f)

            with versioned_file.stage_version('version1') as g:
                g.create_dataset('data',
                                 data=np.arange(10000).reshape((100, 10, 10)),
                                 chunks=(3, 3, 3))

        self.file = h5py.File('bench.hdf5', 'a')
        self.versioned_file = VersionedHDF5File(self.file)

    def teardown(self):
        self.file.close()
        os.remove('bench.hdf5')

    def time_getattr(self):
        dataset = self.versioned_file['version1']['data']
        assert isinstance(dataset, InMemoryDataset)
        dataset[:, 0, 0:6]

    def time_setattr(self):
        with self.versioned_file.stage_version('version2') as g:
            dataset = g['data']
            assert isinstance(dataset, InMemoryDataset)
            dataset[:, 0, 0:6] = -1

    def time_resize_bigger(self):
        with self.versioned_file.stage_version('version2') as g:
            dataset = g['data']
            assert isinstance(dataset, InMemoryDataset)
            dataset.resize((100, 100, 100))

    def time_resize_smaller(self):
        with self.versioned_file.stage_version('version2') as g:
            dataset = g['data']
            assert isinstance(dataset, InMemoryDataset)
            dataset.resize((10, 10, 10))
