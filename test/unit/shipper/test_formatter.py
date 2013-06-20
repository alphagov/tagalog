from ...helpers import assert_equal
import json
from tagalog.shipper.formatter import (elasticsearch_bulk_decorate,
                                       format_as_json,
                                       format_as_elasticsearch_bulk_json)

def test_elasticsearch_bulk_decorate():
    output = elasticsearch_bulk_decorate('logs-index',
                                         'message',
                                         '{"@message": "this is a test string"}')

    lines = output.splitlines()
    assert_equal({'index': {'_type': 'message', '_index': 'logs-index'}},
                 json.loads(lines[0]))
    assert_equal({'@message': 'this is a test string'}, json.loads(lines[1]))


def test_format_as_elasticsearch_bulk_json():
    output = format_as_elasticsearch_bulk_json('keyname',
                                               'typename',
                                               {'@message': 'test string'})

    lines = output.splitlines()
    assert_equal({'index': {'_type': 'typename', '_index': 'keyname'}},
                 json.loads(lines[0]))
    assert_equal({'@message': 'test string'}, json.loads(lines[1]))


def test_format_as_json():
    output = format_as_json({'@message':'test string'})

    assert_equal({'@message': 'test string'}, json.loads(output))

