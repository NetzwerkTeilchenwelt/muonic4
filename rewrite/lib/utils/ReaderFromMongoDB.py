from mongoengine import connect
import zmq
from datetime import datetime, timezone
from .db.RecordAdapter import RecordAdapter
import jsonpickle
import threading


class ReaderFromMongoDB(object):
    """
    Class that read data from MongoDB and sends it as if it were coming from a DAQ card.
    This is a basic version, which can be extended.
    Inits the MongoDB connection and the zeromq socket. This needs to start before any analysis.
    """

    def __init__(self):
        # connect to MongoDB
        connect('muonic', host='localhost', port=27017,
                username="root", password="muonic", authentication_source='admin')
        # setup zmq socket for the server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://*:1234")

    def run(self):
        """
        Get data from a certain timeframe from the db and then sends it through the socket.
        """
        # Set up the MongoDB aggregation pipeline for time based filtering
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
            # convert objects retrieved from the db into Record objects and send them via zmq
            rec = RecordAdapter(**o)
            self.socket.send_string(jsonpickle.encode(rec.createRecord()))

    def setup_channel(self, ch0, ch1, ch2, ch3, coincidence):
        """
        Fake function. Just for API compatibility
        """
        print(f"Setting up fake channel: {ch0, ch1, ch2, ch3, coincidence}")

    def set_threashold(self, ch0, ch1, ch2, ch3):
        """
        Fake function. Just for API compatibility
        """
        print(f"setting fake threshold: {ch0, ch1, ch2, ch3}")

    def setRunning(self, state):
        """
        Fake function. Just for API compatibility
        """
        print(f"setting fake running: {state}")

    def reset_scalars(self):
        """
        Fake function. Just for API compatibility
        """
        print("resettig fake scalars")

    def start_reading_data(self):
        """
        Fake function. Just for API compatibility
        """
        print("starting to send data")
        x = threading.Thread(target=self.run)
        x.setDaemon(True)
        x.start()

    def read_scalars(self):
        """
        Fake function. Just for API compatibility
        """
        print("reading fake scalars")

    def do(self, arg):
        """
        Fake function. Just for API compatibility
        """
        print(f"Doing fake {arg}")

    def get_temp_and_pressure(self):
        """
        Fake function. Just for API compatibility
        """
        print("getting fake temp and pressure")

    def clear_queues(self):
        """
        Fake function. Just for API compatibility
        """
        print("clearing non existing queues")

    def stop_reading_data(self):
        """
        Fake function. Just for API compatibility
        """
        print("stopping reading fake data")
