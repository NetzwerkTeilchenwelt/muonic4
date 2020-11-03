from lib.utils.ReaderFromMongoDB import ReaderFromMongoDB
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


def run():
    with SimpleXMLRPCServer(('localhost', 5556), requestHandler=RequestHandler, allow_none=True) as server:
        server.register_introspection_functions()
        server.register_instance(ReaderFromMongoDB())
        server.serve_forever()


if __name__ == "__main__":
    run()
