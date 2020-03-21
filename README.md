# Autothrottle

There isn't much to setup.
Python 3.7+ should work, 
install requirements from requirements.txt


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

because this seems like a good approximation of how servers can implement rate limiting algorithms
Therefore mimicking that should perform generally well.

#### TODO
