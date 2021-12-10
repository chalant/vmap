import os

from os import path

from gscrap.data import paths

from gscrap.image_capture import video_reader as vr
from gscrap.sampling import utils

_PATH = paths.tmp()

try:
    os.mkdir(_PATH)
except FileExistsError:
    pass

def get_instance_samples(rectangle_instance):
    return RectangleInstanceSamples(rectangle_instance)

class RectangleInstanceSamples(object):
    def __init__(self, rectangle_instance):
        #read from a file written with the expected format, where
        # the first 16 bytes are the byte size of each frame
        # and the second 16 bytes are the num of samples.

        self._rectangle_instance = rectangle_instance

        self._file = None

        self._path = fp = path.join(
            _PATH,
            rectangle_instance.id)

        #read tail of the file that contains metadata of the samples

        with open(fp, 'rb') as f:
            f.seek(-16, 2)

            self._byte_size = int.from_bytes(f.read(8), 'little')
            self._num_samples = int.from_bytes(f.read(8), 'little')

    @property
    def num_samples(self):
        return self._num_samples

    def get_sample(self, index):
        if index < self._num_samples:
            file = self._file

            byte_size = self._byte_size

            file.seek(index * byte_size)

            return file.read(byte_size)
        else:
            raise IndexError

    def __getitem__(self, item):
        return self.get_sample(item)

    def __len__(self):
        return self._num_samples

    def __enter__(self):
        self.open()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        self._file = open(
            path.join(_PATH, self._rectangle_instance.id),
            "rb")

    def close(self):
        self._file.close()
        self._file = None

def clear_samples(rectangle_instance_id):
    os.remove(path.join(paths.tmp(), rectangle_instance_id))

def store_samples(rectangle_instance_id, stream):
    #write samples stream into a path.

    with open(path.join(paths.tmp(), rectangle_instance_id), 'ab') as f:
        num_frames = 1

        itr = iter(stream)

        first_frame = next(itr)

        bytes_size = len(first_frame)

        f.write(first_frame)

        for s in itr:
            num_frames += 1
            f.write(s)

        f.write(int.to_bytes(bytes_size, 8, "little"))
        f.write(int.to_bytes(num_frames, 8, "little"))

def load_samples_with_limit(video_metadata, bbox, from_=0, max_frames=200):

    #todo: problem: this might get really big
    # might need to use memory mapping, or some form of compression

    # dict for tracking already sampled elements
    samples = {}

    read_process = vr.create_read_process(video_metadata, from_, bbox)

    i = 0

    for bytes_ in read_process.read():
        if bytes_ not in samples:
            samples[bytes_] = i

            i += 1

            if i <= max_frames:
                yield bytes_
            else:
                read_process.terminate()

def load_all_samples(video_metadata, bbox, from_=0):
    # dict for tracking already sampled elements
    samples = {}

    read_process = vr.create_read_process(video_metadata, from_, bbox)

    i = 0

    for bytes_ in read_process.read():
        if bytes_:
            if bytes_ not in samples:
                samples[bytes_] = i

                yield bytes_
        else:
            read_process.terminate()

def compress_samples(samples, num_samples, equal_fn=None):
    uf = utils.UnionFind(num_samples)

    if not equal_fn:
        return uf.indices

    #todo: could optimize this

    for i in range(0, num_samples - 1):
        s0 = samples[i]
        for j in range(1, len(samples)):
            if equal_fn(s0, samples[j]):
                uf.union(i, j)

    return uf.indices
