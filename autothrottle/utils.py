from datetime import datetime
from enum import Enum


class TimeInterval(Enum):
    SECOND = "%Y/%m/%d %H:%M:%S"
    MINUTE = "%Y/%m/%d %H:%M"
    HOUR = "%Y/%m/%d %H"
    DAY = "%Y/%m/%d"


def get_timestamp_key(t: datetime, degree: TimeInterval):
    return t.strftime(degree.value)



