from lib.utils.WriterToMongoDB import WriterToMongoDB


def run():
    w = WriterToMongoDB()

    w.runDaemon()


if __name__ == "__main__":
    run()
