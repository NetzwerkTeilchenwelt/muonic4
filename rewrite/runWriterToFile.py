from lib.utils.WriterToFile import WriterToFile
from datetime import datetime


def run():
    """
    Writes incoming data to a file. Default filename format is: %Y-%m-%d_%H-%M-%S_F.txt 
    """
    w = WriterToFile()
    print(
        f'Writing to file {datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}_F.txt\nWhen done quit with CTRL-C.')
    w.runDaemon()


if __name__ == "__main__":
    run()
