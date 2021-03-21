import abc


class BaseKhuJob:

    _metaclass = abc.ABCMeta

    @abc.abstractmethod
    def process(self, data):
        pass

class BaseKhuException(Exception):
    def __init__(self, message):
        self.message = message
