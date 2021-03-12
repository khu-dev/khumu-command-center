import abc


class BaseKhuJob:

    _metaclass = abc.ABCMeta

    @abc.abstractmethod
    def request(self, body_data):
        pass

    @abc.abstractmethod
    def process(self, body_html):
        pass