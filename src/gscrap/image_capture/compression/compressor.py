import chunk
import lzma

import threading

import compression_pb2 as cp

class Compressor(object):
    def __init__(self):
        self._interrupt = False
        self._done = threading.Event()

    def compress(
            self,
            input_file,
            output_file,
            frame_byte_size,
            frames_per_write,
            cursor,
            max_size):

        self._done.clear()

        compressor = lzma.LZMACompressor()

        ipt = open(input_file, "rb")
        opt = open(output_file, "wb")

        interrupted = False
        finished = False

        bytes = b""
        size = 0

        chunk_size = frame_byte_size * frames_per_write

        #start from this point in file
        ipt.seek(cursor * chunk_size)

        cur = cursor

        while True:
            if self._interrupt:
                interrupted = True
                break

            data = ipt.read(chunk_size)

            if not data:
                finished = True
                break

            res = compressor.compress(data)

            bytes += res
            size += len(res)

            cur += frames_per_write

            if size >= max_size:
                break

        #only write if the compression was not interrupted
        if not interrupted:
            bytes += compressor.flush()
            opt.write(bytes)
            opt.close()

        ipt.close()

        self._done.set()

        return finished, interrupted, size, cur

    def join(self):
        self._done.wait()

    def interrupt(self):
        self._interrupt = True