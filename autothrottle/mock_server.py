from autothrottle.servers import AbstractServer
from http import HTTPStatus
import time
from autothrottle.utils import TimeInterval, get_timestamp_key
from datetime import datetime
import logging


class Mock429ErrorServer(AbstractServer):

    def __init__(self, request_limit=60, time_interval=60, **kwargs):
        super(Mock429ErrorServer, self).__init__(**kwargs)
        self.request_limit = request_limit
        self.time_interval = time_interval
        self.request_history = {}

    def request(self, requester=None):
        if requester is None:
            return HTTPStatus.FORBIDDEN
        request_count, start_time = self.request_history.get(requester, 0)
        if start_time < time.time() - self.time_interval:
            self.__reset_history__(requester)
            return HTTPStatus.OK
        if request_count > self.request_limit:
            return HTTPStatus.TOO_MANY_REQUESTS
        self.request_history[requester] = (request_count + 1, start_time)
        return HTTPStatus.OK

    def __reset_history__(self, requester):
        self.request_history[requester] = (1, time.time())


class MockFixedInterval429ErrorServer(AbstractServer):

    def __init__(self, request_limit=5, time_interval: TimeInterval = TimeInterval.SECOND, **kwargs):
        super(MockFixedInterval429ErrorServer, self).__init__(**kwargs)
        self.request_limit = request_limit
        self.time_interval = time_interval
        self.request_history = {}

    def request(self, requester=None):
        if requester is None:
            return HTTPStatus.FORBIDDEN
        request_count, start_time = self.request_history.get(requester, (0, get_timestamp_key(datetime.now(), self.time_interval)))
        if start_time != get_timestamp_key(datetime.now(), self.time_interval):
            self.__reset_history__(requester)
            return HTTPStatus.OK
        if request_count > self.request_limit:
            print(logging.INFO, "responding with 429.")
            return HTTPStatus.TOO_MANY_REQUESTS
        self.request_history[requester] = (request_count + 1, start_time)
        return HTTPStatus.OK

    def __reset_history__(self, requester):
        self.request_history[requester] = (1, get_timestamp_key(datetime.now(), self.time_interval))


