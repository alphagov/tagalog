from ...helpers import assert_equal
from tagalog.shipper.formatter import elasticsearch_bulk_decorate

def test_elasticsearch_bulk_decorate():
    output = elasticsearch_bulk_decorate('logs-index', 'message', '{"@message": "this is a test string"}')

    assert_equal(output, '{"index": {"_type": "message", "_index": "logs-index"}}\n{"@message": "this is a test string"}\n')
