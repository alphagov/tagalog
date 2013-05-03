from ...helpers import assert_equal
from tagalog.shipper.formatter import elasticsearch_bulk_decorate, format_as_json, format_as_elasticsearch_bulk_json

def test_elasticsearch_bulk_decorate():
    output = elasticsearch_bulk_decorate('logs-index', 'message', '{"@message": "this is a test string"}')

    assert_equal(output, '{"index": {"_type": "message", "_index": "logs-index"}}\n{"@message": "this is a test string"}\n')


def test_format_as_elasticsearch_bulk_json():
    output = format_as_elasticsearch_bulk_json('keyname','typename',{'@message':'test string'})

    assert_equal(output, '{"index": {"_type": "typename", "_index": "keyname"}}\n{"@message": "test string"}\n')


def test_format_as_json():
    output = format_as_json({'@message':'test string'})

    assert_equal(output, '{"@message": "test string"}')

