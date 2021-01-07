from concurrent import futures

POOL = futures.ThreadPoolExecutor()

def load(callback):
    POOL.submit(callback)

def store(store_fn):
    POOL.submit(store_fn)

def execute(fn):
    POOL.submit(fn)