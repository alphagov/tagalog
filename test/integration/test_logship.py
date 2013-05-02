from ..helpers import assert_equal, assert_true, TimestampRange
from subprocess import Popen, PIPE
from mock import patch, MagicMock
from tagalog.command import logship

import json
import socket


def test_defaults():
    p = Popen('logship -s stdout', shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input='hello'.encode("utf-8"))
    json_out = json.loads(data_out.decode("utf-8"))
    assert_equal('hello', json_out['@message'])
    assert_true('@timestamp' in json_out)
    assert_true('@source_host' in json_out)


def test_elasticsearch_bulk_format():
    p = Popen('logship -f init_txt -s stdout --bulk --bulk-index logs-current',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input='hello'.encode("utf-8"))

    assert_equal('{"index": {"_type": "message", "_index": "logs-current"}}\n{"@message": "hello"}\n\n',
                 data_out.decode("utf-8"))

def test_add_tags():
    p = Popen('logship -s stdout -f init_txt,add_tags:handbags:great',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input='hello'.encode("utf-8"))
    assert_equal({'@message': 'hello', '@tags': ['handbags', 'great']},
                 json.loads(data_out.decode("utf-8")))


def test_fields():
    p = Popen('logship -s stdout -f init_txt,add_fields:handbags=great:why=because',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input='hello'.encode("utf-8"))
    assert_equal({'@message': 'hello', '@fields': {'handbags': 'great', 'why': 'because'}},
                 json.loads(data_out.decode("utf-8")))


def test_json_timestamp_generated():
    input_dict = {'@fields': {'handbags': 'great', 'why': 'because'}}

    tsrange = TimestampRange()
    with tsrange:
        p = Popen('logship -s stdout -f init_json,add_timestamp',
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

    p = Popen('logship -f init_json -s stdout',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input=json.dumps(input_dict).encode("utf-8"))
    assert_equal(input_dict, json.loads(data_out.decode("utf-8")))


def test_json_tags():
    input_dict = {
      '@timestamp': '2013-01-01T09:00:00.000000Z',
      '@fields': {'handbags': 'great', 'why': 'because'},
      '@tags': ['handbags'],
    }

    p = Popen('logship -f init_json,add_tags:why -s stdout',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input=json.dumps(input_dict).encode("utf-8"))

    input_dict['@tags'].append('why')
    assert_equal(input_dict, json.loads(data_out.decode("utf-8")))


def test_json_fields():
    input_dict = {
      '@timestamp': '2013-01-01T09:00:00.000000Z',
      '@fields': {'handbags': 'great', 'why': 'because'},
    }

    p = Popen('logship -f init_json,add_fields:cannot=comprehend -s stdout',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input=json.dumps(input_dict).encode("utf-8"))

    input_dict['@fields']['cannot'] = 'comprehend'
    assert_equal(input_dict, json.loads(data_out.decode("utf-8")))


def test_json_source_host():
    input_dict = {
      '@timestamp': '2013-01-01T09:00:00.000000Z',
      '@messages': 'Callithrix, Cebuella, Callibella, and Mico',
    }

    p = Popen('logship -f init_json,add_source_host -s stdout',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input=json.dumps(input_dict).encode("utf-8"))

    input_dict['@source_host'] = socket.getfqdn()
    assert_equal(input_dict, json.loads(data_out.decode("utf-8")))

### redis shipper tests ###

@patch('tagalog.shipper.ResilientStrictRedis')
def test_redis_shipper(redis_mock):
    fake_lines = MagicMock()
    fake_lines.return_value = iter([u'rawLogLine\n'])

    with patch("tagalog.io.lines", fake_lines):
        with patch("sys.argv", ['logship', '-f','init_txt','-k','redis_key']):
            logship.main()

            redis_mock.return_value.lpush.assert_called_with(u'redis_key', '{"@message": "rawLogLine"}')
