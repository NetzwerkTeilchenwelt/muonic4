from mongoengine import connect
import zmq
from datetime import datetime, timezone
from .db.RecordAdapter import RecordAdapter
import jsonpickle
import threading


class ReaderFromMongoDB(object):
    def __init__(self):
        connect('muonic', host='localhost', port=27017,
                username="root", password="muonic", authentication_source='admin')
        # setup zmq socket for the server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://*:1234")

    def run(self):
        pipeline = [
            {
                '$match': {
                    'timestamp': {
                        '$gt': datetime(2020, 10, 28, 0, 0, 0, tzinfo=timezone.utc),
                        '$lt': datetime(2020, 10, 30, 0, 0, 0, tzinfo=timezone.utc)
                    }
                }
            }
        ]
        objs = RecordAdapter.objects().aggregate(pipeline)
        for o in list(objs):
            rec = RecordAdapter(**o)
            self.socket.send_string(jsonpickle.encode(rec.set()))

    def setup_channel(self, ch0, ch1, ch2, ch3, coincidence):
        print(f"Setting up fake channel: {ch0, ch1, ch2, ch3, coincidence}")

    def set_threashold(self, ch0, ch1, ch2, ch3):
        print(f"setting fake threshold: {ch0, ch1, ch2, ch3}")

    def setRunning(self, state):
        print(f"setting fake running: {state}")

    def reset_scalars(self):
        print("resettig fake scalars")

    def start_reading_data(self):
        print("starting to send data")
        x = threading.Thread(target=self.run)
        x.setDaemon(True)
        x.start()

    def read_scalars(self):
        print("reading fake scalars")

    def do(self, arg):
        print(f"Doing fake {arg}")

    def get_temp_and_pressure(self):
        print("getting fake temp and pressure")

    def clear_queues(self):
        print("clearing non existing queues")

    def stop_reading_data(self):
        print("stopping reading fake data")
