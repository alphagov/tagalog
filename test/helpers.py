import os

from mock import *
from nose.tools import *
from datetime import datetime

HERE = os.path.dirname(__file__)


def fixture(*path):
    return open(fixture_path(*path), 'rb')


def fixture_path(*path):
    return os.path.join(HERE, 'fixtures', *path)


class TimestampRange(object):
    """
    Helper for timestamp creations which can't be mocked.

    Provides a ``with`` context manager which can be used to wrap operations
    that generate a timestamp. When complete, a resulting timestamp string
    can be passed to ``assert_in_range(string)`` in order to assert that it
    falls within the start and finish time of the context. All times should
    be ISO8601 UTC.
    """
    def __init__(self):
        self.lower = None
        self.upper = None

    def __enter__(self):
        self.lower = datetime.utcnow()

    def __exit__(self, type, value, traceback):
        self.upper = datetime.utcnow()

    def assert_in_range(self, ts_string):
        ts = datetime.strptime(ts_string, '%Y-%m-%dT%H:%M:%S.%fZ')
        assert_true(self.lower < ts < self.upper)
