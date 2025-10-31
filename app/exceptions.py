class ClamAVException(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return str(self.message)


class ArchiveException(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return str(self.message)


class FileTooBigException(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return str(self.message)
