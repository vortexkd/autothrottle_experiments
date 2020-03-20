from abc import ABC, abstractmethod
from autothrottle.mock_server import AbstractServer
from http import HTTPStatus
from datetime import datetime
import time
import logging

"""
There are 4 common intervals used for api rate limits that are considered here.
Per second, Per Minute, Per Hour, Per Day (per month limits are unlikely to be fixed at the throttler level).

In implementing these there are 2 possible strategies that can be used to measure the time.
1) Fixed interval measurement. 
-> N requests per minute is measured for each minute, so theoretically you could have up to 2N requests within
 a 60 second interval without bad responses, if you started requests at 30s past the minute mark.
2) Measurement from first request time.
-> I dont think this is very common, but the idea is that the clock starts on the first request, and from that time a time interval T is measured
within which a maximum of N requests can be made.

"""
class AutoThrottledRequester:

    def __init__(self, name='AutoThrottledRequester', initial_delay=1):
        self.name = name
        self.delay = initial_delay
        self.request_history = {}
        self.delay_estimates = {}  # server, interval, number, confidence?

    def run_requests(self, server: AbstractServer, number_of_requests=60):
        print('running requests')
        for i in range(number_of_requests):
            print("request: {}".format(i))
            response = server.request(requester=self.name)
            self.add_to_history(server, response)
            if response == HTTPStatus.TOO_MANY_REQUESTS:
                self.increase_delay()
            if self.delay:
                time.sleep(self.delay)
            yield response

    def increase_delay(self):
        pass

    def add_to_history(self, server, response):
        if server.name not in self.request_history.keys():
            self.request_history[server.name] = [(datetime.now(), response)]
        else:
            self.request_history[server.name].append((datetime.now(), response))


class DelayStrategy(ABC):

    def __init__(self, **kwargs):
        super(DelayStrategy, self).__init__(**kwargs)
