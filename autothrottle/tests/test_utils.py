from unittest import TestCase
from ..utils import get_seconds_until_end_of_interval, TimeInterval
from datetime import datetime


class TestTimer(TestCase):

    def test_seconds_remaining(self):
        d = datetime(year=2020, month=3, day=5, hour=10, minute=6, second=12)
        assert 1 == get_seconds_until_end_of_interval(d, TimeInterval.SECOND)
        assert 48 == get_seconds_until_end_of_interval(d, TimeInterval.MINUTE)
        assert (53 * 60) + 48 == get_seconds_until_end_of_interval(d, TimeInterval.HOUR)
        assert (13 * 3600) + (53 * 60) + 48 == get_seconds_until_end_of_interval(d, TimeInterval.DAY)