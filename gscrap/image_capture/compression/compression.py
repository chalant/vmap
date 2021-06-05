import os

import queue

import threading
import subprocess

import psutil

import grpc

import compression_pb2_grpc as cpg
import compression_pb2 as cp

#maximum number of processes leave one core available
MAX_PROCESSES = psutil.cpu_count(False) - 1

class CompressorClient(object):
    def __init__(self, address, max_bytes):
        """

        Parameters
        ----------
        address
        max_bytes
        """
        self._stub = cpg.CompressorStub(grpc.insecure_channel(address))

        #create a subprocess
        self._server = subprocess.Popen(
            ["python",
             "gscrap/image_capture/compression/server.py",
             address,
             "compression"])

        self._max_bytes = max_bytes

    def interrupt(self):
        #terminate process immediatly
        self._server.terminate()

    def stop(self):
        #stop server
        #wait until end of compression
        self._stub.Join(cp.JoinRequest())

        self._server.terminate()
        #wait until process finishes

    def compress(self, input_file, output_dir, byte_size):
        stub = self._stub
        max_bytes = self._max_bytes

        output_file = os.path.join(output_dir, '0')

        reply = stub.Compress(
            cp.CompressionRequest(
                input_file=input_file,
                output_file=output_file,
                byte_size=byte_size,
                cursor=0,
                max_byte_size=max_bytes,
        ))

        i = 1

        while not reply.finished:
            if reply.interrupted:
                #remove file if compression interrupted
                os.remove(output_file)
                return

            output_file = os.path.join(output_dir, '{}'.format(i))

            reply = stub.Compress(
                cp.CompressionRequest(
                    input_file=input_file,
                    output_file=output_file,
                    byte_size=byte_size,
                    cursor=reply.cursor,
                    max_byte_size=max_bytes
                )
            )

        #todo: if was interrupted, save cursor and byte size so that we can resume compression
        #todo: we need to increment output_file number
        #todo: build index data


class Compression(object):
    def __init__(self, max_processes=None):
        """

        Parameters
        ----------
        thread_pool: concurrent.futures.ThreadPoolExecutor
        max_processes
        """

        self._max_processes = mp = max_processes if max_processes else MAX_PROCESSES
        self._queue = q = queue.Queue(mp)
        self._compressors = []

        address = "[::]:5005{}"

        compressors = self._compressors

        #start compressor servers
        for i in range(mp):
            compressor = CompressorClient(address.format(i + 1))
            q.put(compressor)
            compressors.append(compressor)


    def compress(self, input_file, output_dir, byte_size):
        thread = threading.Thread(
            target=self._launch_compression,
            args=(input_file, output_dir, byte_size))

        thread.start()

    def stop(self, wait=True):
        if wait:
            #wait for processes to terminate
            threads = []
            for compressor in self._compressors:
                thread = threading.Thread(target=compressor.stop)

                threads.append(thread)
                thread.start()

            #wait for termination

            for thread in threads:
                thread.join()

        else:
            for compressor in self._compressors:
                compressor.interrupt()

    def _launch_compression(self, input_file, output_file, byte_size):
        q = self._queue

        compressor = q.get() #will block until a process is available

        if compressor.compress(input_file, output_file, byte_size):
            #remove input file if the compression was successful
            os.remove(input_file)

        q.put(compressor)