import click
import compression_pb2_grpc as cpg
import compression_pb2 as cp

import server_utils

import compressor

class CompressorService(cpg.CompressorServicer):
    def __init__(self):
        self._compressor = compressor.Compressor()

    def Compress(self, request, context):
        finished, interrupted, size, cursor = self._compressor.compress(
            request.input_file,
            request.output_file,
            request.byte_size,
            request.frames_per_write,
            request.cursor,
            request.max_size)

        return cp.CompressionReply(
            finished=finished,
            interrupted=interrupted,
            size=size,
            cursor=cursor
        )

    def Join(self, request, context):
        #blocks until the compressor is done
        self._compressor.join()

        return cp.JoinReply()

    def interrupt(self):
        self._compressor.interrupt()

class DecompressorService(cpg.DecompressorServicer):
    def __init__(self):
        pass

    def Decompress(self, request, context):
        pass

    def Join(self, request, context):
        pass

SERVER = server_utils.get_server()

@click.command()
@click.argument('address')
@click.argument('service')
def start_server(address, service):
    server = server_utils.get_server()

    svc = None

    if service == 'compression':
        svc = CompressorService()
        cpg.add_CompressorServicer_to_server(svc, server)

    elif service  == 'decompression':
        svc = DecompressorService()
        cpg.add_DecompressorServicer_to_server(svc, server)

    if svc == None:
        raise ValueError("{} service is not supported".format(service))

    server.start(address, svc)

if __name__ == '__main__':
    start_server()
