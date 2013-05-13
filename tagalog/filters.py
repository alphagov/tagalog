"""
The :mod:`filters` Module contains the definitions for the filters supported by
``logtag`` and ``logship``, as well as a number of functions used to construct
the filter chains.

A filter is a generator function which takes an iterable as its first argument,
and optionally takes additional configuration arguments. It returns a generator
yielding the filtered log lines.
"""

import csv
import datetime
import itertools
import json
import socket
import logging

FILTERS = {}

log = logging.getLogger(__name__)

class FilterError(Exception):
    pass


def pipeline(*functions):
    """
    Construct a filter pipeline from a list of filter functions

    Given a list of functions taking an iterable as their only argument, and
    which return a generator, this function will return a single function with the
    same signature, which applies each function in turn for each item in the
    iterable, yielding the results.

    That is, given filter functions ``a``, ``b``, and ``c``, ``pipeline(a, b,
    c)`` will return a function which yields ``c(b(a(x)))`` for each item ``x``
    in the iterable passed to it. For example:

    >>> def a(iterable):
    ...     for item in iterable:
    ...         yield item + ':a'
    ...
    >>> def b(iterable):
    ...     for item in iterable:
    ...         yield item + ':b'
    ...
    >>> pipe = pipeline(a, b)
    >>> data_in = ["foo", "bar"]
    >>> data_out = pipe(data_in)
    >>> [x for x in data_out]
    ['foo:a:b', 'bar:a:b']
    """
    head = functions[0]
    tail = functions[1:]
    if tail:
        def _fn(iterable):
            for i in pipeline(*tail)(head(iterable)):
                yield i
        return _fn
    else:
        return head


def build(description):
    """Build a filter chain from a filter description string"""
    filters = next(csv.reader([description]))
    filter_funcs = [get(f[0], f[1:]) for f in csv.reader(filters, delimiter=':')]
    return pipeline(*filter_funcs)


def get(name, args=[]):
    """
    Get a filter function from a filter name and a list of unparsed arguments
    """
    try:
        f = FILTERS[name]
    except KeyError:
        raise FilterError('No such filter: {0}'.format(name))

    f_args = []
    f_kwargs = {}

    for arg in args:
        a = arg.split('=', 1)
        if len(a) == 1:
            f_args.append(a[0])
        else:
            f_kwargs[a[0]] = a[1]

    # Construct the curried filter function
    def _filterfunc(iterable):
        for item in f(iterable, *f_args, **f_kwargs):
            yield item

    return _filterfunc


def init_txt(iterable):
    """
    Read lines of text from ``iterable`` and yield dicts with the line data
    stored in the ``@message`` field.

    >>> data_in = ["hello\\n", "world\\n"]
    >>> data_out = init_txt(data_in)
    >>> [x for x in data_out]
    [{'@message': 'hello'}, {'@message': 'world'}]
    """
    for line in iterable:
        txt = line.rstrip('\n')
        yield {'@message': txt}
FILTERS['init_txt'] = init_txt


def init_json(iterable):
    """
    Read lines of JSON text from ``iterable`` and parse each line as a JSON
    object. Yield dicts for each line that successfully parses as a JSON object.
    Unparseable events will be skipped and raise a warning.

    >>> data_in = ['{"@message": "one message"}', '{"@message": "another message"}']
    >>> data_out = init_json(data_in)
    >>> [x for x in data_out]
    [{u'@message': u'one message'}, {u'@message': u'another message'}]
    """
    for line in iterable:
        try:
            item = json.loads(line)
        except ValueError as e:
            log.warn('init_json: could not parse JSON message "{0}"'.format(line))
            log.warn('init_json: error was "{0}"'.format(e))
            continue

        if not isinstance(item, dict):
            log.warn('init_json: skipping message "{0}" (not a JSON object)'.format(line))
            continue

        yield item
FILTERS['init_json'] = init_json


def add_timestamp(iterable, override=False):
    """
    Compute an accurate timestamp for each item in ``iterable``, adding an
    accurate timestamp to each one when received. The timestamp is a
    usecond-precision ISO8601 string added to the ``@timestamp`` field.

    By default, existing ``@timestamp`` fields will not be overwritten. This
    behaviour can be toggled with the ``override`` argument.

    >>> data_in = [{'@message': 'one message'}, {'@message': 'another message'}]
    >>> data_out = add_timestamp(data_in)
    >>> [x for x in data_out]
    [{'@timestamp': '2013-05-13T10:37:56.766743Z', '@message': 'one message'},
     {'@timestamp': '2013-05-13T10:37:56.767185Z', '@message': 'another message'}]
    """
    k = '@timestamp'
    for item in iterable:
        if override or k not in item:
            item[k] = now()
        yield item
FILTERS['add_timestamp'] = add_timestamp


def add_source_host(iterable, override=False):
    """
    Add the FQDN of the current machine to the ``@source_host`` field of each
    item in ``iterable``.

    By default, existing ``@source_host`` fields will not be overwritten. This
    behaviour can be toggled with the ``override`` argument.

    >>> data_in = [{'@message': 'one message'}, {'@message': 'another message'}]
    >>> data_out = add_source_host(data_in)
    >>> [x for x in data_out]
    [{'@source_host': 'lynx.local', '@message': 'one message'},
     {'@source_host': 'lynx.local', '@message': 'another message'}]
    """
    k = '@source_host'
    source_host = socket.getfqdn()
    for item in iterable:
        if override or k not in item:
            item[k] = source_host
        yield item
FILTERS['add_source_host'] = add_source_host


def add_fields(iterable, **kw_fields):
    """
    Add fields to each item in ``iterable``. Each key=value pair provided is
    merged into the ``@fields`` object, which will be created if required.

    >>> data_in = [{'@message': 'one message'}, {'@message': 'another message'}]
    >>> data_out = add_fields(data_in, foo='bar', baz='qux')
    >>> [x for x in data_out]
    [{'@fields': {'foo': 'bar', 'baz': 'qux'}, '@message': 'one message'},
     {'@fields': {'foo': 'bar', 'baz': 'qux'}, '@message': 'another message'}]
    """
    k = '@fields'
    for item in iterable:
        if k not in item:
            item[k] = {}
        item[k].update(kw_fields)
        yield item
FILTERS['add_fields'] = add_fields


def add_tags(iterable, *taglist):
    """
    Add tags to each item in ``iterable``. Each tag is added to the ``@tags``
    array, which will be created if required.

    >>> data_in = [{'@message': 'one message'}, {'@message': 'another message'}]
    >>> data_out = add_tags(data_in, 'foo', 'bar')
    >>> [x for x in data_out]
    [{'@message': 'one message', '@tags': ['foo', 'bar']},
     {'@message': 'another message', '@tags': ['foo', 'bar']}]
    """
    k = '@tags'
    for item in iterable:
        try:
            item[k].extend(taglist)
        except (AttributeError, KeyError):
            item[k] = []
            item[k].extend(taglist)
        yield item
FILTERS['add_tags'] = add_tags


def parse_lograge(iterable):
    """
    Attempt to parse each dict or dict-like object in ``iterable`` as if it were
    in lograge format, (e.g. "status=200 path=/users/login time=125ms"), adding
    key-value pairs to '@fields' for each matching item.

    >>> data_in = [{'@message': 'path=/foo/bar status=200 time=0.060'},
    ...            {'@message': 'path=/baz/qux status=503 time=1.651'}]
    >>> data_out = parse_lograge(data_in)
    >>> [x for x in data_out]
    [{'@fields': {'status': '200', 'path': '/foo/bar', 'time': '0.060'}, '@message': 'path=/foo/bar status=200 time=0.060'},
     {'@fields': {'status': '503', 'path': '/baz/qux', 'time': '1.651'}, '@message': 'path=/baz/qux status=503 time=1.651'}]
    """
    for item in iterable:
        if '@message' not in item:
            log.warn('parse_lograge: skipping item missing "@message" key ("{0}")'.format(item))
            continue
        if '@fields' not in item:
            item['@fields'] = {}
        for kv in item['@message'].split():
            ret = kv.split('=', 1)
            if len(ret) == 2:
                item['@fields'][ret[0]] = ret[1]
        yield item
FILTERS['parse_lograge'] = parse_lograge


def now():
    return _now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def _now():
    return datetime.datetime.utcnow()


