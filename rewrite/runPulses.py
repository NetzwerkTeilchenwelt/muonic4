from lib.analyzers.PulseAnalyzer import PulseAnalyzer


def run():
    """
    Creates an instance of RateAnalyzer and runs a simple rate measurement.
    """
    r = PulseAnalyzer()
    r.measure_pulses(meastime=1.0)


if __name__ == "__main__":
    run()
