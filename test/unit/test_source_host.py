from ..helpers import assert_equal, patch
import datetime
from tagalog import source_host


def test_no_source_host():
    data = [{'@message': 'one'},
            {'@message': 'two'},
            {'@message': 'three'}]
    out = source_host(data)

    assert_equal(next(out), {'@message': 'one', '@source_host': None})
    assert_equal(next(out), {'@message': 'two', '@source_host': None})
    assert_equal(next(out), {'@message': 'three', '@source_host': None})


def test_source_host_provided():
    data = [{'@message': 'one'},
            {'@message': 'two'},
            {'@message': 'three'}]
    out = source_host(data, source_host='chimpanzee.zoo.tld')

    assert_equal(next(out), {'@source_host': 'chimpanzee.zoo.tld', '@message': 'one'})
    assert_equal(next(out), {'@source_host': 'chimpanzee.zoo.tld', '@message': 'two'})
    assert_equal(next(out), {'@source_host': 'chimpanzee.zoo.tld', '@message': 'three'})


def test_source_host_provided_custom_key():
    data = [{'@message': 'one'},
            {'@message': 'two'},
            {'@message': 'three'}]
    out = source_host(data, source_host='orangutan.zoo.tld', key='host')

    assert_equal(next(out), {'host': 'orangutan.zoo.tld', '@message': 'one'})
    assert_equal(next(out), {'host': 'orangutan.zoo.tld', '@message': 'two'})
    assert_equal(next(out), {'host': 'orangutan.zoo.tld', '@message': 'three'})


def test_source_host_existing():
    data = [{'@source_host': 'orangutan.zoo.tld', '@message': 'one'},
            {'@source_host': 'orangutan.zoo.tld', '@message': 'two'},
            {'@source_host': 'orangutan.zoo.tld', '@message': 'three'}]
    out = source_host(data)

    assert_equal(next(out), {'@source_host': 'orangutan.zoo.tld', '@message': 'one'})
    assert_equal(next(out), {'@source_host': 'orangutan.zoo.tld', '@message': 'two'})
    assert_equal(next(out), {'@source_host': 'orangutan.zoo.tld', '@message': 'three'})


def test_source_host_dont_overwrite_existing():
    data = [{'@source_host': 'orangutan.zoo.tld', '@message': 'one'},
            {'@source_host': 'orangutan.zoo.tld', '@message': 'two'},
            {'@source_host': 'orangutan.zoo.tld', '@message': 'three'}]
    out = source_host(data, source_host='chimpanzee.zoo.tld')

    assert_equal(next(out), {'@source_host': 'orangutan.zoo.tld', '@message': 'one'})
    assert_equal(next(out), {'@source_host': 'orangutan.zoo.tld', '@message': 'two'})
    assert_equal(next(out), {'@source_host': 'orangutan.zoo.tld', '@message': 'three'})
