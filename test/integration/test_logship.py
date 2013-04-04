from ..helpers import assert_equal
from nose.plugins.skip import SkipTest
from subprocess import Popen, PIPE
import json


def test_tags():
    p = Popen('logship --no-stamp -s stdout -t handbags great',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input='hello')
    assert_equal({'@message': 'hello', '@tags': ['handbags', 'great']},
                 json.loads(data_out.decode("utf-8")))


def test_fields():
    p = Popen('logship --no-stamp -s stdout -f handbags=great why=because',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input='hello')
    assert_equal({'@message': 'hello', '@fields': { 'handbags': 'great', 'why': 'because'}},
                 json.loads(data_out.decode("utf-8")))


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


def test_json_tags():
    json_input = '{"@timestamp": "2013-01-01T09:00:00.000000Z", "@fields": {"handbags": "great", "why": "because"}, "@tags": ["handbags"]}'
    p = Popen('logship --json -s stdout -t why',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input=json_input)
    assert_equal({'@timestamp': '2013-01-01T09:00:00.000000Z', '@fields': { 'handbags': 'great', 'why': 'because'}, '@tags': ['handbags', 'why']},
                 json.loads(data_out.decode("utf-8")))


def test_json_fields():
    json_input = '{"@timestamp": "2013-01-01T09:00:00.000000Z", "@fields": {"handbags": "great", "why": "because"}}'
    p = Popen('logship --json -s stdout -f cannot=comprehend',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input=json_input)
    assert_equal({'@timestamp': '2013-01-01T09:00:00.000000Z', '@fields': { 'handbags': 'great', 'why': 'because', 'cannot': 'comprehend'}},
                 json.loads(data_out.decode("utf-8")))
