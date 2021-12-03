from gscrap.image_capture import video_reader as vr
from gscrap.sampling import utils

def load_samples(video_metadata, bbox, from_=0, max_frames=200):

    #todo: problem: this might get really big
    # might need to use memory mapping, or some from of compression

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
