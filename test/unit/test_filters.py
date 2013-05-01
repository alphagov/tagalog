from ..helpers import assert_equal, assert_raises, patch
import datetime
from tagalog.filters import FilterError
from tagalog.filters import pipeline, get, build
from tagalog.filters import init_txt, init_json
from tagalog.filters import add_fields, add_tags, add_timestamp, add_source_host
from tagalog.filters import parse_lograge


def test_pipeline():
    items = []
    calls = []
    def _make_filter(name):
        def _f(iterable):
            for i in iterable:
                calls.append(name + ':' + i)
                yield i
        return _f

    p = pipeline(_make_filter('a'), _make_filter('b'), _make_filter('c'))
    for item in p(['one', 'two', 'three']):
        items.append(item)

    assert_equal(['one', 'two', 'three'], items)
    assert_equal(['a:one', 'b:one', 'c:one',
                  'a:two', 'b:two', 'c:two',
                  'a:three', 'b:three', 'c:three'], calls)


def test_get_simple():
    p = get('init_txt')

    out = list(p(['one', 'two']))
    assert_equal([{'@message': 'one'}, {'@message': 'two'}], out)


def test_get_nonexistent_filter():
    assert_raises(FilterError, get, 'wibble')


def test_get_args():
    p = get('add_tags', ['foo'])

    out = list(p([{}]))
    assert_equal([{'@tags': ['foo']}], out)


def test_get_kwargs():
    p = get('add_fields', ['foo=bar'])

    out = list(p([{}]))
    assert_equal([{'@fields': {'foo': 'bar'}}], out)


def test_build():
    p = build('init_txt,add_tags:foo,add_fields:bar=qux')

    out = list(p(['hello\n']))
    assert_equal([{'@message': 'hello',
                   '@tags': ['foo'],
                   '@fields': {'bar': 'qux'}}], out)


def test_init_txt():
    res = init_txt(['foo\n', 'bar\n', 'baz\n'])
    assert_equal({'@message': 'foo'}, next(res))
    assert_equal({'@message': 'bar'}, next(res))
    assert_equal({'@message': 'baz'}, next(res))


def test_init_json():
    lines = [
      '{"@fields": {"text": "foo"}}\n',
      '{"@fields": {"text": "bar"}}\n',
      '{"@fields": {"text": "baz"}}\n',
    ]

    res = init_json(lines)
    assert_equal({'@fields': {'text': 'foo'}}, next(res))
    assert_equal({'@fields': {'text': 'bar'}}, next(res))
    assert_equal({'@fields': {'text': 'baz'}}, next(res))


@patch('tagalog.filters.log.warn')
def test_init_json_invalid_json(warn_mock):
    lines = [
      '{"@fields": {"text": "foo"}}\n',
      'I am not json\n',
      '{"@fields": {"text": "baz"}}\n',
    ]

    res = init_json(lines)
    assert_equal({'@fields': {'text': 'foo'}}, next(res))
    assert_equal({'@fields': {'text': 'baz'}}, next(res))

    warn_mock.assert_called()


@patch('tagalog.filters.log.warn')
def test_init_json_json_but_not_object(warn_mock):
    lines = [
      '{"@fields": {"text": "foo"}}\n',
      '["hello", "world"]\n',
      '{"@fields": {"text": "baz"}}\n',
    ]

    res = init_json(lines)
    assert_equal({'@fields': {'text': 'foo'}}, next(res))
    assert_equal({'@fields': {'text': 'baz'}}, next(res))

    warn_mock.assert_called()


def test_add_fields_no_fields():
    data = [{'@message': 'one'},
            {'@message': 'two'}]
    out = add_fields(data)

    assert_equal({'@message': 'one', '@fields': {}}, next(out))
    assert_equal({'@message': 'two', '@fields': {}}, next(out))


def test_add_fields_single_field():
    data = [{'@message': 'one'},
            {'@message': 'two'}]
    out = add_fields(data, foobar='baz')

    assert_equal({'@message': 'one', '@fields': {'foobar': 'baz'}}, next(out))
    assert_equal({'@message': 'two', '@fields': {'foobar': 'baz'}}, next(out))


def test_add_fields_multiple_fields():
    data = [{'@message': 'one'},
            {'@message': 'two'}]
    out = add_fields(data, foobar='baz', sausage='bacon')

    assert_equal({'@message': 'one', '@fields': {'foobar': 'baz',
                                                 'sausage': 'bacon'}},
                 next(out))
    assert_equal({'@message': 'two', '@fields': {'foobar': 'baz',
                                                 'sausage': 'bacon'}},
                 next(out))


def test_add_fields_existing_fields_are_overwritten():
    data = [{'@message': 'hello',
             '@fields': {'existing': 'field', 'untouched': 'field'}}]
    out = add_fields(data, existing='wood')

    assert_equal({'@message': 'hello', '@fields': {'existing': 'wood',
                                                   'untouched': 'field'}},
                 next(out))


def test_add_tags_no_tags():
    data = [{'@message': 'one'},
            {'@message': 'two'}]
    out = add_tags(data, 'foobar', 'baz')

    assert_equal({'@message': 'one', '@tags': ['foobar', 'baz']}, next(out))
    assert_equal({'@message': 'two', '@tags': ['foobar', 'baz']}, next(out))


def test_add_tags_appends_tags():
    data = [{'@message': 'one', '@tags': ['wibble']},
            {'@message': 'two', '@tags': []}]
    out = add_tags(data, 'foobar', 'baz')

    assert_equal({'@message': 'one', '@tags': ['wibble', 'foobar', 'baz']},
                 next(out))
    assert_equal({'@message': 'two', '@tags': ['foobar', 'baz']},
                 next(out))


def test_add_tags_dont_tag():
    data = [{'@message': 'one'},
            {'@message': 'two'}]
    out = add_tags(data)

    assert_equal({'@message': 'one', '@tags': []}, next(out))
    assert_equal({'@message': 'two', '@tags': []}, next(out))


def test_add_tags_replaces_nonextendable_value():
    data = [{'@message': 'one', '@tags': 'a string'}]
    out = add_tags(data, 'foobar', 'baz')

    assert_equal({'@message': 'one', '@tags': ['foobar', 'baz']}, next(out))

    data = [{'@message': 'one', '@tags': None},
            {'@message': 'two', '@tags': None}]
    out = add_tags(data, 'foobar', 'baz')

    assert_equal({'@message': 'one', '@tags': ['foobar', 'baz']}, next(out))
    assert_equal({'@message': 'two', '@tags': ['foobar', 'baz']}, next(out))


@patch('tagalog.filters._now')
def test_add_timestamp(now_mock):
    now_mock.side_effect = [datetime.datetime(2013, 1, 1, 9, 0, 1, 0),
                            datetime.datetime(2013, 1, 1, 9, 0, 2, 100),
                            datetime.datetime(2013, 1, 1, 9, 0, 3, 200)]

    data = [{'@message': 'one'},
            {'@message': 'two'},
            {'@message': 'three'}]
    out = add_timestamp(data)
    assert_equal({'@timestamp': '2013-01-01T09:00:01.000000Z',
                  '@message': 'one'},
                 next(out))
    assert_equal({'@timestamp': '2013-01-01T09:00:02.000100Z',
                  '@message': 'two'},
                 next(out))
    assert_equal({'@timestamp': '2013-01-01T09:00:03.000200Z',
                  '@message': 'three'},
                 next(out))


def test_add_timestamp_leaves_existing_timestamp():
    data = [{'@timestamp': '2013-01-01T09:00:01.000000Z', 'msg': 'one'},
            {'@timestamp': '2013-01-01T09:00:02.000100Z', 'msg': 'two'},
            {'@timestamp': '2013-01-01T09:00:03.000200Z', 'msg': 'three'}]

    out = add_timestamp(data)
    assert_equal({'@timestamp': '2013-01-01T09:00:01.000000Z',
                  'msg': 'one'},
                 next(out))
    assert_equal({'@timestamp': '2013-01-01T09:00:02.000100Z',
                  'msg': 'two'},
                 next(out))
    assert_equal({'@timestamp': '2013-01-01T09:00:03.000200Z',
                  'msg': 'three'},
                 next(out))


@patch('tagalog.filters.socket.getfqdn')
def test_add_source_host(fqdn_mock):
    data = [{'@message': 'one'},
            {'@message': 'two'},
            {'@message': 'three'}]
    out = add_source_host(data)

    fqdn_mock.return_value = 'orangutan.zoo.tld'

    assert_equal({'@source_host': 'orangutan.zoo.tld', '@message': 'one'}, next(out))
    assert_equal({'@source_host': 'orangutan.zoo.tld', '@message': 'two'}, next(out))
    assert_equal({'@source_host': 'orangutan.zoo.tld', '@message': 'three'}, next(out))


def test_add_source_host_doesnt_overwrite_existing():
    data = [{'@source_host': 'orangutan.zoo.tld', '@message': 'one'},
            {'@source_host': 'orangutan.zoo.tld', '@message': 'two'},
            {'@source_host': 'orangutan.zoo.tld', '@message': 'three'}]
    out = add_source_host(data)

    assert_equal({'@source_host': 'orangutan.zoo.tld', '@message': 'one'}, next(out))
    assert_equal({'@source_host': 'orangutan.zoo.tld', '@message': 'two'}, next(out))
    assert_equal({'@source_host': 'orangutan.zoo.tld', '@message': 'three'}, next(out))


def test_parse_lograge():
    data = [{'@message': 'status=200 keys=1,2,3 method=GET'},
            {'@message': 'status=403 data that is not lograge formatted'},
            {'@message': 'data that is not lograge formatted'}]
    out = parse_lograge(data)

    assert_equal({'status': '200', 'keys': '1,2,3', 'method': 'GET'}, next(out)['@fields'])
    assert_equal({'status': '403'}, next(out)['@fields'])
    assert_equal({}, next(out)['@fields'])


@patch('tagalog.filters.log.warn')
def test_parse_lograge_no_message(warn_mock):
    data = [{'@message': 'status=200 keys=1,2,3 method=GET'},
            {},
            {'@message': 'status=403 data that is not lograge formatted'}]
    out = parse_lograge(data)

    assert_equal({'status': '200', 'keys': '1,2,3', 'method': 'GET'}, next(out)['@fields'])
    assert_equal({'status': '403'}, next(out)['@fields'])

    warn_mock.assert_called()
