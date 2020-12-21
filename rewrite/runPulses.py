from lib.analyzers.PulseAnalyzer import PulseAnalyzer


def run():
    """
    Creates an instance of PulseAnalyzer and runs a simple pulse measurement.
    """
    r = PulseAnalyzer()
    print("Starting pulse analysis. When done quit with CTRL-C.")
    r.measure_pulses(meastime=1.0)


if __name__ == "__main__":
    run()
