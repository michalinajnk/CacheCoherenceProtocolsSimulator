import os

class Logger:
    """
    A simple logger class that writes messages to a file.
    """
    def __init__(self, filename: str, overwrite: bool = True):
        if os.path.exists(filename) and overwrite:
            os.remove(filename)
        self.file = open(filename, 'w')

    def write(self, message):
        self.file.write(message)

    def close(self):
        self.file.close()