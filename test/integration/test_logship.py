from ..helpers import assert_equal
from nose.plugins.skip import SkipTest
from subprocess import Popen, PIPE
import json


def test_tags():
    p = Popen('logship --no-stamp -s stdout -t handbags great',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input='hello'.encode("utf-8"))
    assert_equal({'@message': 'hello', '@tags': ['handbags', 'great']},
                 json.loads(data_out.decode("utf-8")))


def test_fields():
    p = Popen('logship --no-stamp -s stdout -f handbags=great why=because',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input='hello'.encode("utf-8"))
    assert_equal({'@message': 'hello', '@fields': { 'handbags': 'great', 'why': 'because'}},
                 json.loads(data_out.decode("utf-8")))


def test_source_host():
    p = Popen('logship --no-stamp -s stdout --source_host gorilla.zoo.tld',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input='hello'.encode("utf-8"))
    assert_equal({'@source_host': 'gorilla.zoo.tld', '@message': 'hello'},
                 json.loads(data_out.decode("utf-8")))


def test_json_timestamp_generated():
    # Skipped until we figure out a way to mock tagalog._now() as
    # datetime.datetime(2013, 1, 1, 9, 0, 0, 0). I suspect it's not possible
    # with the use of subprocess to spawn a separate interpreter.
    raise SkipTest

    input_dict = {
      '@fields': {'handbags': 'great', 'why': 'because'}
    }

    p = Popen('logship --json -s stdout',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input=json.dumps(input_dict).encode("utf-8"))

    input_dict['@timestamp'] = '2013-01-01T09:00:00.000000Z'
    assert_equal(input_dict, json.loads(data_out.decode("utf-8")))


def test_json_timestamp_included():
    input_dict = {
      '@timestamp': '2013-01-01T09:00:00.000000Z',
      '@fields': {'handbags': 'great', 'why': 'because'},
    }

    p = Popen('logship --json -s stdout',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input=json.dumps(input_dict).encode("utf-8"))
    assert_equal(input_dict, json.loads(data_out.decode("utf-8")))


def test_json_tags():
    input_dict = {
      '@timestamp': '2013-01-01T09:00:00.000000Z',
      '@fields': {'handbags': 'great', 'why': 'because'},
      '@tags': ['handbags'],
    }

    p = Popen('logship --json -s stdout -t why',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input=json.dumps(input_dict).encode("utf-8"))

    input_dict['@tags'].append('why')
    assert_equal(input_dict, json.loads(data_out.decode("utf-8")))


def test_json_fields():
    input_dict = {
      '@timestamp': '2013-01-01T09:00:00.000000Z',
      '@fields': {'handbags': 'great', 'why': 'because'},
    }

    p = Popen('logship --json -s stdout -f cannot=comprehend',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input=json.dumps(input_dict).encode("utf-8"))

    input_dict['@fields']['cannot'] = 'comprehend'
    assert_equal(input_dict, json.loads(data_out.decode("utf-8")))


def test_json_source_host():
    input_dict = {
      '@timestamp': '2013-01-01T09:00:00.000000Z',
      '@messages': 'Callithrix, Cebuella, Callibella, and Mico',
    }

    p = Popen('logship --json -s stdout --source-host marmoset.zoo.tld',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input=json.dumps(input_dict).encode("utf-8"))

    input_dict['@source_host'] = 'marmoset.zoo.tld'
    assert_equal(input_dict, json.loads(data_out.decode("utf-8")))
