import abc


class BaseKhuJob:

    _metaclass = abc.ABCMeta

    @abc.abstractmethod
    def process(self, data):
        pass