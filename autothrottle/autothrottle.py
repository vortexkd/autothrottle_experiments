from abc import ABC, abstractmethod
from autothrottle.mock_server import AbstractServer
from autothrottle.utils import TimeInterval, SlidingWindow, get_parts, get_next_interval, get_seconds, get_time_part, \
    get_seconds_until_end_of_interval
from http import HTTPStatus
from datetime import datetime
import time
from typing import Tuple


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

    def __init__(self, name='AutoThrottledRequester', initial_delay=1, concurrent_threads=1):
        self.name = name
        self.delay = initial_delay
        self.rate_limit_reset_delay = 0
        self.request_history = {}
        self.delay_estimates = {}
        self.delay_intervals = {}
        self.possible_intervals = (TimeInterval.SECOND, TimeInterval.MINUTE, TimeInterval.HOUR, TimeInterval.DAY)
        self.__initial_failover_lives__ = max(3, concurrent_threads + 2)  # TODO: better logic for this redundancy?
        self.failover_lives = max(3, concurrent_threads + 2)

    def run_requests(self, server: AbstractServer, number_of_requests=60):
        """
        :param server: the entity to sent requests to.
        :param number_of_requests: the number of requests to send in total. (This would be, say, a list of urls or something).
        :return: responses from the server.
        """
        for i in range(number_of_requests):
            print("request: {}".format(i))
            before_sent = datetime.now()
            # request time delta latency TODO: mock server with latency simulation.
            response = server.request(requester=self.name)
            # estimation of when the server received the response.
            sent_at = datetime.now() - (datetime.now() - before_sent) / 2
            history = self.add_to_history(server, sent_at, response)
            if response == HTTPStatus.TOO_MANY_REQUESTS:
                self.increase_delay(server, sent_at, self.get_delay_interval(server), history)
            else:
                self.failover_lives = self.__initial_failover_lives__
            yield response
            if self.rate_limit_reset_delay:
                time.sleep(self.rate_limit_reset_delay)
                self.rate_limit_reset_delay = 0
            elif self.delay:
                time.sleep(self.delay * get_seconds(self.get_delay_interval(server)))

        print(self.request_history)

    def increase_delay(self, server, sent_at, time_slot: TimeInterval, history: Tuple[SlidingWindow]):
        # 1. estimate request rate, # 2. estimate the request rate -1.
        if self.failover_lives <= 0:
            time_slot = get_next_interval(time_slot)
            self.delay_intervals[server.name] = time_slot
            self.failover_lives = self.__initial_failover_lives__
        wanted_rate = (history[0].previous_count * ((get_parts(time_slot) - get_time_part(sent_at, time_slot))
                                                    / get_parts(time_slot))) \
                       + history[0].current_count - 1
        # 3. calculate delay required to achieve that rate.
        self.delay = 1 / wanted_rate
        print("setting delay to: {}".format(self.delay), time_slot)
        self.wait_until_end_of_time_slot(sent_at, time_slot)
        self.failover_lives -= 1

    def wait_until_end_of_time_slot(self, sent_at: datetime, time_slot: TimeInterval):
        self.rate_limit_reset_delay = get_seconds_until_end_of_interval(sent_at, time_slot)


    def get_delay_interval(self, server):
        return self.delay_intervals.get(server.name, TimeInterval.SECOND)

    def add_to_history(self, server, sent_at, res):
        if res == HTTPStatus.OK:
            if server.name not in self.request_history.keys():
                self.request_history[server.name] = (SlidingWindow(TimeInterval.SECOND, sent_at),
                                                     SlidingWindow(TimeInterval.MINUTE, sent_at),
                                                     SlidingWindow(TimeInterval.HOUR, sent_at),
                                                     SlidingWindow(TimeInterval.DAY, sent_at))
            else:
                for struct in self.request_history[server.name]:
                    struct.add_request(sent_at)
        return self.request_history[server.name]

