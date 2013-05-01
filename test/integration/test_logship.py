from ..helpers import assert_equal, TimestampRange
from subprocess import Popen, PIPE

import json


def test_tags():
    p = Popen('logship --no-stamp -s stdout -t handbags great',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input='hello'.encode("utf-8"))
    assert_equal({'@message': 'hello', '@tags': ['handbags', 'great']},
                 json.loads(data_out.decode("utf-8")))


def test_elasticsearch_bulk_format():
    p = Popen('logship --no-stamp -s stdout --bulk --bulk-index logs-current',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input='hello'.encode("utf-8"))

    assert_equal('{"index": {"_type": "message", "_index": "logs-current"}}\n{"@message": "hello"}\n\n',
                 data_out.decode("utf-8"))

def test_fields():
    p = Popen('logship --no-stamp -s stdout -f handbags=great why=because',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input='hello'.encode("utf-8"))
    assert_equal({'@message': 'hello', '@fields': { 'handbags': 'great', 'why': 'because'}},
                 json.loads(data_out.decode("utf-8")))


def test_source_host():
    p = Popen('logship --no-stamp -s stdout --source-host gorilla.zoo.tld',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input='hello'.encode("utf-8"))
    assert_equal({'@source_host': 'gorilla.zoo.tld', '@message': 'hello'},
                 json.loads(data_out.decode("utf-8")))


def test_json_timestamp_generated():
    input_dict = {
      '@fields': {'handbags': 'great', 'why': 'because'}
    }

    tsrange = TimestampRange()
    with tsrange:
        p = Popen('logship --json -s stdout',
                  shell=True, stdout=PIPE, stdin=PIPE)
        data_out, _ = p.communicate(input=json.dumps(input_dict).encode("utf-8"))

    output_dict = json.loads(data_out.decode("utf-8"))
    output_ts = output_dict.pop('@timestamp')
    assert_equal(input_dict, output_dict)
    tsrange.assert_in_range(output_ts)


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
