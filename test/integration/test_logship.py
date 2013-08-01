from socket import socket, AF_INET, SOCK_DGRAM, getfqdn
from subprocess import Popen, PIPE
from mock import patch, MagicMock
import json

from ..helpers import assert_equal, assert_true, assert_regexp_matches, TimestampRange
from tagalog.command import logship


def test_defaults():
    p = Popen('logship -s stdout', shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input='hello'.encode("utf-8"))
    json_out = json.loads(data_out.decode("utf-8"))
    assert_equal('hello', json_out['@message'])
    assert_true('@timestamp' in json_out)
    assert_true('@source_host' in json_out)


def test_elasticsearch_bulk_format():
    p = Popen('logship -f init_txt -s stdout,bulk=true,bulk_index=logs-current',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input='hello'.encode("utf-8"))

    lines = data_out.decode("utf-8").splitlines()
    assert_equal({'index': {'_type': 'message', '_index': 'logs-current'}},
                 json.loads(lines[0]))
    assert_equal({'@message': 'hello'}, json.loads(lines[1]))


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

    input_dict['@source_host'] = getfqdn()
    assert_equal(input_dict, json.loads(data_out.decode("utf-8")))


def test_statsd_shipper():
    input_dict = {
      '@source_host': 'fred-flintstone',
      '@fields.status': 500,
    }

    sock = _udp_socket()
    try:
        p = Popen('logship -s statsd,metric=%{@source_host}.%{@fields.status} -f init_json', shell=True, stdout=PIPE, stdin=PIPE)
        p.communicate(input=json.dumps(input_dict).encode("utf-8"))

        data = sock.recv(1024)

        assert_equal(data, "fred-flintstone.500:1|c".encode('utf-8'))
    finally:
        sock.close()


def test_statsd_timer_shipper():
    input_dict = {
      '@source_host': 'fred-flintstone',
      '@fields.status': 500,
      '@fields.request_time': 40.25,
    }

    sock = _udp_socket()
    try:
        p = Popen('logship -s statsd_timer,metric=%{@source_host}.request_time,timed_field=@fields.request_time -f init_json', shell=True, stdout=PIPE, stdin=PIPE)
        p.communicate(input=json.dumps(input_dict).encode("utf-8"))

        data = sock.recv(1024)

        assert_regexp_matches(data, r"^fred-flintstone.request_time:40.250*\|ms$".encode('utf-8'))
    finally:
        sock.close()


def test_stdout_and_statsd_shipper():
    input_dict = { '@source_host': 'road-runner' }

    sock = _udp_socket()
    try:
        p = Popen('logship -s statsd,metric=%{@source_host} stdout -f init_json', shell=True,
                stdout=PIPE, stdin=PIPE)

        result_stdout, _ = p.communicate(input=json.dumps(input_dict).encode("utf-8"))
        result_statsd = sock.recv(1024)

        assert_equal(result_statsd, "road-runner:1|c".encode('utf-8'))
        assert_equal(json.loads(result_stdout.decode('utf-8')), input_dict)
    finally:
        sock.close()


def _udp_socket():
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(("127.0.0.1", 8125))
    sock.settimeout(0.2)

    return sock
