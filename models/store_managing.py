from concurrent import futures

POOL = futures.ThreadPoolExecutor(1)

class StoreManager(object):
    def write(self, data):
        pass

    def read(self, data, listeners):
        pass