#todo: samples are extracted from footage.  We run accross the footage, and we extract
# samples of capture zones that share the same rectangle.
# we then group elements together by how similar they are according to some threshold
# and by applying some filters

# once all that is done, we can start labeling elements if they are classifiable.
# Labeled elements will be saved as templates (training data).

# only samples in the capture zone should be loaded. So that we know what zone to adjust
# if filters don't work properly.

#1) load samples from video
#2) apply filters
#3) do union-find based on "distance (difference)"

from gscrap.image_capture import video_reader as vr
from gscrap.sampling import utils

def load_samples(video_metadata, bbox):

    #todo: problem: this might get really big
    # might need to use memory mapping, or some from of compression

    # dict for tracking already sampled elements
    samples = {}

    for bytes_ in vr.read(video_metadata, crop=bbox):
        i = 0

        if bytes_ not in samples:
            samples[bytes_] = i

            i += 1

            yield bytes_

def compress_samples(samples, num_samples, equal_fn=None):
    uf = utils.UnionFind(num_samples)

    if not equal_fn:
        return uf.indices

    #todo: could optimize this

    for i in range(0, len(samples - 1)):
        s0 = samples[i]
        for j in range(1, len(samples)):
            if equal_fn(s0, samples[j]):
                uf.union(i, j)

    return uf.indices
