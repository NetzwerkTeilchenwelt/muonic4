from lib.utils.ReaderFromFile import ReaderFromFile
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler


class RequestHandler(SimpleXMLRPCRequestHandler):
    """
    Adapter Class for xmlrpc
    """
    rpc_paths = ('/RPC2',)


def run():
    """
    Starts an instance of the DAQ server with xmlrpc enabled and then enters an infinite loop
    """
    with SimpleXMLRPCServer(('localhost', 5556), requestHandler=RequestHandler, allow_none=True) as server:
        server.register_introspection_functions()
        server.register_instance(ReaderFromFile("test_data.txt"))
        server.serve_forever()


if __name__ == "__main__":
    run()
