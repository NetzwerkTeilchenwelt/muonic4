from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from lib.daq.DAQServer import DAQServer


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


with SimpleXMLRPCServer(('localhost', 5556), requestHandler=RequestHandler, allow_none=True) as server:
    server.register_introspection_functions()
    server.register_instance(DAQServer())
    server.serve_forever()
