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


def pipeline(head, *tail):
    """Construct a filter pipeline from a list of functions"""
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
    Read lines of text from the iterable ``iterable`` and yield dicts with the
    line data stored in the key given by ``key`` (default: "@message").
    """
    for line in iterable:
        txt = line.rstrip('\n')
        yield {'@message': txt}
FILTERS['init_txt'] = init_txt


def init_json(iterable):
    """
    Read lines of JSON input from the iterable ``iterable`` and yield dicts.
    Each event must be on a single line. Unparseable events will be skipped and
    raise a warning.
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


def now():
    return _now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def _now():
    return datetime.datetime.utcnow()


def add_timestamp(iterable, override=False):
    """
    Compute an accurate timestamp for item in ``iterable``, adding an accurate
    timestamp to each one when received. The timestamp is a usecond-precision
    ISO8601 string. The timestamp is added to each dict with a key set by
    ``key`` unless the dict already contains its own.
    """
    k = '@timestamp'
    for item in iterable:
        if override or k not in item:
            item[k] = now()
        yield item
FILTERS['add_timestamp'] = add_timestamp


def add_source_host(iterable, override=False):
    """
    Add the source host for each dict or dict-like object in ``iterable``.
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
    merged into the '@fields' object, which will be created if required.
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
    Add tags to each item in ``iterable``. Each tag is added to the '@tags'
    array, which will be created if required.
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
