from ..helpers import assert_equal
from nose.plugins.skip import SkipTest
from subprocess import Popen, PIPE
import json


def test_json_timestamp_generated():
    # Skipped until we figure out a way to mock tagalog._now() as
    # datetime.datetime(2013, 1, 1, 9, 0, 0, 0). I suspect it's not possible
    # with the use of subprocess to spawn a separate interpreter.
    raise SkipTest

    json_input = '{"@fields": {"handbags": "great", "why": "because"}}'
    p = Popen('logship --json -s stdout',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input=json_input)
    assert_equal({'@timestamp': '2013-01-01T09:00:00.000000Z', '@fields': { 'handbags': 'great', 'why': 'because'}},
                 json.loads(data_out.decode("utf-8")))


def test_json_timestamp_included():
    json_input = '{"@timestamp": "2013-01-01T09:00:00.000000Z", "@fields": {"handbags": "great", "why": "because"}}'
    p = Popen('logship --json -s stdout',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input=json_input)
    assert_equal({'@timestamp': '2013-01-01T09:00:00.000000Z', '@fields': { 'handbags': 'great', 'why': 'because'}},
                 json.loads(data_out.decode("utf-8")))
