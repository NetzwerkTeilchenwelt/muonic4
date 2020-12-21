from lib.utils.WriterToMongoDB import WriterToMongoDB


def run():
    w = WriterToMongoDB()
    print("Starting writer to DB. When done quit with CTRL-C")
    w.runDaemon()


if __name__ == "__main__":
    run()
