import os

from mock import *
from nose.tools import *
from datetime import datetime

HERE = os.path.dirname(__file__)


def fixture(*path):
    return open(fixture_path(*path), 'rb')


def fixture_path(*path):
    return os.path.join(HERE, 'fixtures', *path)


class TimestampRange:
    """
    Helper for timestamp creations which can't be mocked. Call ``start()`
    and ``finish()`` either side of the method which creates the timestamp.
    Then call ``assert_inrange(string)`` with the timestamp string that you
    want to test. It will assert that it is within the upper and lower bands
    expected. Times should be ISO8601 UTC.
    """
    def __init__(self):
        self.lower = None
        self.upper = None

    def start(self):
        self.lower = datetime.utcnow()

    def finish(self):
        self.upper = datetime.utcnow()

    def assert_inrange(self, ts_string):
        ts = datetime.strptime(ts_string, '%Y-%m-%dT%H:%M:%S.%fZ')
        assert(self.lower < ts)
        assert(self.upper > ts)
