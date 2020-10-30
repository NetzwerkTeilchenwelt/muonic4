from lib.analyzers.RateAnalyzer import RateAnalyzer


def run():

    r = RateAnalyzer()

    r.measure_rates(timewindow=10.0, meastime=1.0)


if __name__ == "__main__":
    run()
