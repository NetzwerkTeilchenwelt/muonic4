import zmq
import time
import jsonpickle
from lib.common.Record import Record
from lib.common.CountRecord import CountRecord
import xmlrpc.client
import threading


def reciever_loop():
    ctx = zmq.Context()
    sock = ctx.socket(zmq.SUB)
    sock.connect("tcp://127.0.0.1:1234")
    sock.subscribe("")  # Subscribe to all topics
    print("Starting receiver loop... Quit with CTRL-C")
    while True:
        msg = sock.recv_string()
        obj = jsonpickle.decode(msg)
        #print(f"OBJ type {type(obj)}")
        print(
            f"Type: {obj.type} timestamp: {obj.timestamp} payloads: {repr(obj.payload)}")

    sock.close()
    ctx.term()


def run():
    t = threading.Thread(target=reciever_loop)
    t.setDaemon(True)
    t.start()

    # s = xmlrpc.client.ServerProxy("http://localhost:5556")

    # # print(s.system.listMethods())

    # s.setup_channel(True, True, True, True, 'threefold')

    # s.set_threashold(110, 110, 180, 110)

    # #s.measure_rates(10.0, 1.0)

    while True:
        pass


if __name__ == "__main__":
    run()
