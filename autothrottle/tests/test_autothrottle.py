from unittest import TestCase
from ..utils import TimeInterval
from ..servers import AbstractServer
from ..mock_server import MockFixedInterval429ErrorServer, Mock429ErrorServer
from ..autothrottle import AutoThrottledRequester


class TestAutoThrottleWithFixedInterval(TestCase):

    def setUp(self) -> None:
        server_cls = MockFixedInterval429ErrorServer   # can try this with Mock429Server as well.
        pass

    def test_fixed_interval_server_minute(self):
        self._run_tests(MockFixedInterval429ErrorServer(request_limit=12, time_interval=TimeInterval.MINUTE))

    def test_fixed_interval_server_second(self):
        self._run_tests(MockFixedInterval429ErrorServer(request_limit=12, time_interval=TimeInterval.SECOND))

    def test_moving_interval_server_second(self):
        self._run_tests(Mock429ErrorServer(request_limit=12, time_interval=TimeInterval.MINUTE))

    def test_moving_interval_server_hour(self):
        self._run_tests(Mock429ErrorServer(request_limit=12, time_interval=TimeInterval.HOUR))

    def _run_tests(self, server,  initial_delay=0.01, total_requests=None):
        if total_requests is None:
            total_requests = server.request_limit * 3
        req = AutoThrottledRequester(initial_delay=initial_delay)
        responses = req.run_requests(server, number_of_requests=total_requests)
        for each in responses:
            if req.get_delay_interval(server) == server.time_interval and (1 / req.delay)\
                    <= server.request_limit:
                # will not change after hitting this, so breaking here saves testing time.
                break
            pass
        assert req.get_delay_interval(server) == server.time_interval
        assert "{} is too high. Server limit is: {}".format(1/req.delay, server.request_limit), \
            (1 / req.delay) <= server.request_limit
        assert "{} is too low. Server limit is: {}".format(1/req.delay, server.request_limit),\
            (1 / req.delay) >= server.request_limit * 0.9
        # ideally be using at least 90% of the request rate.

