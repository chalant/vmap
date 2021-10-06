import signal

from concurrent import futures

import threading

import grpc

class ServerWrapper(object):
    def __init__(self, num_threads=10):
        self._server = grpc.server(futures.ThreadPoolExecutor(num_threads))
        self._stop = threading.Event()

    def start(self, address, service):
        server = self._server
        server.add_insecure_port(address)

        server.start()
        self._stop.wait()

        service.interrupt()

    def stop(self):
        self._stop.set()

    def add_generic_rpc_handlers(self, handlers):
        self._server.add_generic_rpc_handlers(handlers)

_SERVER = ServerWrapper()

def stop_server(signum, frame):
    if signum == signal.SIGTERM or signum == signal.SIGINT:
        _SERVER.stop()

signal.signal(signal.SIGTERM , stop_server)
signal.signal(signal.SIGINT, stop_server)

def get_server():
    return _SERVER