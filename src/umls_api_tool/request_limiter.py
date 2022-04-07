import datetime
import time

MAX_REQUESTS_PER_SECOND = 20  # Defined: https://documentation.uts.nlm.nih.gov/terms-of-service.html


class TimelyRequestLimiter:
    """Keep track of requests and clock time to ensure that request can be sent."""

    def __init__(self, requests_per_second=MAX_REQUESTS_PER_SECOND):
        self._requests_per_second = requests_per_second
        self._end_time = datetime.datetime.now() + datetime.timedelta(seconds=1)
        self._counter = 0

    def ready(self):
        self._counter += 1
        if self._counter >= self._requests_per_second:
            self._counter = 0
            while datetime.datetime.now() < self._end_time:
                time.sleep(0.02)
            self._end_time = datetime.datetime.now() + datetime.timedelta(seconds=1)


class SleepyRequestLimiter:
    """Always time.sleep before requests to ensure that never sending too many requests."""

    def __init__(self, requests_per_second=MAX_REQUESTS_PER_SECOND):
        self._sleep_time = 1.0 / requests_per_second

    def ready(self):
        time.sleep(self._sleep_time)


class ForgetfulRequestLimiter:
    """No request limiting."""

    def __init__(self, requests_per_second=MAX_REQUESTS_PER_SECOND):
        pass

    def ready(self):
        pass
