import abc


class AbstractProvider:

    def __init__(self, GoogleClient, folder):
        self.googleClient = GoogleClient
        self.folder = folder

    @abc.abstractmethod
    def getStatement(self):
        return