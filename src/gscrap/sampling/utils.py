import cv2

import numpy as np

class UnionFind(object):
    def __init__(self, number_elements):
        self._indices = [i for i in range(number_elements)]
        self._count = number_elements
        self._sizes = [1 for i in range(number_elements)]

    @property
    def count(self):
        return self._count

    @property
    def indices(self):
        return self._indices

    def union(self, p, q):
        i = self.find(p)
        j = self.find(q)

        idc = self._indices
        szs = self._sizes

        if i != j:
            if szs[i] < szs[j]:
                idc[i] = j
                szs[j] += szs[i]
            else:
                idc[j] = i
                szs[i] += szs[j]

        self._count -= 1


    def find(self, p):
        idc = self._indices

        while p != idc[p]:
            p = idc[p]

        return p

def equal(im1, im2, threshold):
    return np.sum(cv2.absdiff(im1, im2) / 255) < threshold