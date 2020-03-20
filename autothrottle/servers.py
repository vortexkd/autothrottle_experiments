from abc import ABC, abstractmethod
from http import HTTPStatus


class AbstractServer(ABC):

    num_servers = 0

    def __init__(self, name='server', **kwargs):
        self.num_servers += 1
        self.name = name + '_{}'.format(self.num_servers)
        super(AbstractServer, self).__init__(**kwargs)

    @abstractmethod
    def request(self, **kwargs) -> HTTPStatus:
        raise NotImplementedError("request() was not implemented.")