import time
from datetime import datetime
from autothrottle.autothrottle import AutoThrottledRequester
from autothrottle.mock_server import MockFixedInterval429ErrorServer, Mock429ErrorServer


print(time.time())
print(datetime.now())

t = datetime.now()
print("{0:0=2d}".format(t.month + 10))
print("{}".format(t.microsecond))

print("starting")
req = AutoThrottledRequester(initial_delay=0.05)
print('here')
server = MockFixedInterval429ErrorServer(request_limit=5)
responses = req.run_requests(server)
for each in responses:
    print(each)
print('done')