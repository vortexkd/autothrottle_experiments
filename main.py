import time
from datetime import datetime
from autothrottle.autothrottle import AutoThrottledRequester
from autothrottle.mock_server import MockFixedInterval429ErrorServer


print(time.time())
print(datetime.now())

t = datetime.now()
print("{0:0=2d}".format(t.month + 10))

print("starting")
req = AutoThrottledRequester(initial_delay=0)
print('here')
server = MockFixedInterval429ErrorServer()
responses = req.run_requests(server)
for each in responses:
    print(each)
print('done')