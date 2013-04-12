from __future__ import unicode_literals
import datetime
import os
import json
import logging

from tagalog import io

__all__ = ['io', 'stamp', 'source_host', 'tag', 'fields']
__version__ = '0.2.6'

# Use UTF8 for stdin, stdout, stderr
os.environ['PYTHONIOENCODING'] = 'utf-8'

log = logging.getLogger(__name__)


def messages(iterable, key='@message'):
    """
    Read lines of UTF-8 from the iterable ``iterable`` and yield dicts with the
    line data stored in the key given by ``key`` (default: "@message").
    """
    for line in iterable:
        txt = line.rstrip('\n')
        yield {key: txt}


def json_messages(iterable):
    """
    Similar to :function:`tagalog.messages` but input is already structured as
    JSON. Each event must be on a single line. Unparseable events will be
    skipped and raise a warning.
    """
    for line in iterable:
        try:
            item = json.loads(line)
        except ValueError as e:
            log.warn('Could not parse JSON message: {0}'.format(e))
            continue

        if not isinstance(item, dict) or not len(item) >= 1:
            log.warn('Skipping message not a dictionary of >=1 length')
            continue

        yield item


def now():
    return  _now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def stamp(iterable, key='@timestamp'):
    """
    Compute an accurate timestamp for each dict or dict-like object in
    ``iterable``, adding an accurate timestamp to each one when received. The
    timestamp is a usecond-precision ISO8601 string. The timestamp is added to
    each dict with a key set by ``key`` unless the dict already contains
    its own.
    """
    for item in iterable:
        if not key in item:
            item[key] = now()
        yield item

def source_host(iterable, source_host=None, key='@source_host'):
    """
    Add the source host for each dict or dict-like object in ``iterable``,
    if it is provided. This can be passed by the app itself, or can be passed
    as a command-line
    argument.
    """
    for item in iterable:
        if source_host != None and not key in item:
            item[key] = source_host
        yield item

def fields(iterable, fields=None):
    """
    Add a set of fields to each item in ``iterable``. The set of fields have a
    key=value format. '@' are added to the front of each key. New fields
    will be merged on top of existing fields.
    """
    if not fields:
        for item in iterable:
            yield item

    prepared_fields = _prepare_fields(fields)

    for item in iterable:
        yield _process_fields(item, prepared_fields)


def _process_fields(item, fields):
    if not '@fields' in item:
        item['@fields'] = {}

    item['@fields'].update(fields)
    return item

def _prepare_fields(fields):
    prepared_fields = {}

    for field in fields:
        split_field = field.split('=', 1)
        if len(split_field) > 1:
          prepared_fields[split_field[0]] = split_field[1][:]
    return prepared_fields


def tag(iterable, tags=None, key='@tags'):
    """
    Add tags to each dict or dict-like object in ``iterable``. Tags are added
    to each dict with a key set by ``key``. If a key already exists under the
    key given by ``key``, this function will attempt to ``.extend()``` it, but
    will fall back to replacing it in the event of error.
    """
    if not tags:
        for item in iterable:
            yield item

    else:
        for item in iterable:
            yield _tag(item, tags, key)


def _now():
    return datetime.datetime.utcnow()


def _tag(item, tags, key):
    if item.get(key):
        try:
            item[key].extend(tags)
            return item
        except (AttributeError, TypeError):
            pass

    item[key] = tags[:]
    return item

