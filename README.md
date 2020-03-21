# Autothrottle

There isn't much to setup.
Python 3.7+ should work, 
install requirements from requirements.txt
The actual autothrottler is in `autothrottle/autothrottle.py`
measuring requests across time frames are managed in `autothrottle/utils.py`
 in the SlidingWindow class


## Ideas / Assumptions
There are 4 common intervals used for api rate limits that are considered here.
Per second, Per Minute, Per Hour, Per Day (per month limits are unlikely to be fixed at the throttler level).

In implementing these there are 2 possible strategies that can be used to measure the time.
1) Fixed interval measurement. 
-> N requests per minute is measured for each minute, so theoretically you could have up to 2N requests within
 a 60 second interval without bad responses, if you started requests at 30s past the minute mark.
2) Measurement from first request time.
-> I dont think this is very common, but the idea is that the clock starts on the first request, and from that time a time interval T is measured
within which a maximum of N requests can be made.


## Solution
There are a couple of ways to solve the issue, including simple remembering all the requests with timestamps 
made making a brute force solution. However, depending on the number of requests,
this could be a performance hit.

I've chosen a Sliding Window Algorithm which i read about here
https://blog.cloudflare.com/counting-things-a-lot-of-different-things/

because this seems like a good approximation of how servers can implement rate limiting algorithms.

The idea is to count requests during the current time interval and store requests for the previous
time interval. in the case of time interval = minutes
The rate can then be estimated by: 

```
# Silding Window rate limit estimation
(requests_in_previous_minute * 
((60 seconds - seconds_completed_in_current_minute) / 60 seconds)
 + requests_in_current_minute)
```
thus assuming a roughly constant rate of requests in the previous interval.

Further
In cases where a rate limit error is encountered, we are aware that any more requests
in the current interval will cause errors, and so we should wait until the end of the interval
before making a new request.


#### TODO
