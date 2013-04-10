from ..helpers import assert_equal, patch
import datetime
from tagalog import source_host

def test_no_source_host_defaults():
    data = [{'@message': 'one'},
            {'@message': 'two'},
            {'@message': 'three'}]
    out = source_host(data)

    assert_equal(next(out), {'@message': 'one', '@source_host': 'default'})
    assert_equal(next(out), {'@message': 'two', '@source_host': 'default'})
    assert_equal(next(out), {'@message': 'three', '@source_host': 'default'})
