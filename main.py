import time
from datetime import datetime
from autothrottle.autothrottle import AutoThrottledRequester
from autothrottle.mock_server import MockFixedInterval429ErrorServer, Mock429ErrorServer
from autothrottle.utils import TimeInterval

requester_initial_delay_interval = 0.01
server_request_limit = 12
server_time_interval = TimeInterval.MINUTE
total_requests = 25

print("starting")
req = AutoThrottledRequester(initial_delay=requester_initial_delay_interval)
print('here')
server = MockFixedInterval429ErrorServer(request_limit=server_request_limit, time_interval=server_time_interval)
responses = req.run_requests(server, number_of_requests=total_requests)
for each in responses:
    print(each)

print(req.delay, req.delay_intervals)