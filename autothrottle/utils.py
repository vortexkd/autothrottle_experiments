from datetime import datetime, timedelta
from enum import Enum


class TimeInterval(Enum):
    SECOND = "%Y/%m/%d %H:%M:%S", 1, 1000000
    MINUTE = "%Y/%m/%d %H:%M", 60, 60
    HOUR = "%Y/%m/%d %H", 3600, 60
    DAY = "%Y/%m/%d", 86400, 24


time_interval_next_map = {TimeInterval.SECOND: TimeInterval.MINUTE, TimeInterval.MINUTE: TimeInterval.HOUR,
                          TimeInterval.HOUR: TimeInterval.DAY}

time_interval_attr = {TimeInterval.SECOND: 'microsecond', TimeInterval.MINUTE: 'second',
                      TimeInterval.HOUR: 'minute', TimeInterval.DAY: 'hour'}


def get_timestamp_key(t: datetime, degree: TimeInterval):
    return t.strftime(degree.value[0])


def get_delta(degree: TimeInterval):
    return timedelta(seconds=degree.value[1])


def get_parts(degree: TimeInterval):
    return degree.value[2]


def get_next_interval(degree: TimeInterval):
    return time_interval_next_map.get(degree, TimeInterval.DAY)


def get_seconds(degree: TimeInterval):
    return degree.value[1]


def get_time_part(time_stamp: datetime, degree: TimeInterval):
    return time_stamp.__getattribute__(time_interval_attr[degree])


def get_seconds_until_end_of_interval(time_stamp: datetime, interval: TimeInterval) -> int:
    # if interval is seconds, return 1.
    # if interval is minutes, return:  get_seconds(1 minute) - current second
    # if interval is hour, return:  get_seconds(1 hour) - (get_seconds(1 minute) * (60 minutes - current_minutes)
    #                               + (60 seconds - current second))
    # if interval is day, return:  get_seconds(1 day) - (get_seconds(1 hour) * (24 hours - current hour) +
    #                               (get_seconds(1 min) * (60 minutes - current_minutes) + (60 seconds - current second))
    spent_time = 0
    if interval == TimeInterval.SECOND:
        return get_seconds(interval) - spent_time
    spent_time += time_stamp.second
    if interval == TimeInterval.MINUTE:
        return get_seconds(interval) - spent_time
    spent_time += time_stamp.minute * get_seconds(TimeInterval.MINUTE)
    if interval == TimeInterval.HOUR:
        return get_seconds(interval) - spent_time
    spent_time += time_stamp.hour * get_seconds(TimeInterval.HOUR)
    return get_seconds(interval) - spent_time


class SlidingWindow:

    """
    This structure implements a sliding window algorithm to estimate the rate of requests over the current time interval.
    It assumes a constant rate of requests over the previous interval.
    """

    def __init__(self, interval: TimeInterval, current: datetime, current_count=1, previous_count=0):
        self.interval = interval
        self.current = current
        self.current_count = current_count
        self.previous_count = previous_count

    def add_request(self, sent_at: datetime):
        label = get_timestamp_key(sent_at, self.interval)
        if label != get_timestamp_key(self.current, self.interval):
            # slide window
            # case 1. next window. case 2, previous window was blank. (no requests in the last interval).
            if self.is_next_window(label):
                self.reset_window(sent_at, self.current_count)
            else:
                self.reset_window(sent_at, 0)
        else:
            self.current_count += 1

    def reset_window(self, new_current, new_previous_count):
        self.current = new_current
        self.current_count = 1
        self.previous_count = new_previous_count

    def is_next_window(self, label: str):
        return get_timestamp_key(self.current + get_delta(self.interval), self.interval) == label

    def __repr__(self):
        return "SlidingWindow: {}\n Current Window: {}\n Current Count{}\n Previous Count{}" \
            .format(self.interval, get_timestamp_key(self.current, self.interval),
                    self.current_count,
                    self.previous_count)

