from __future__ import unicode_literals
import os
import sys
import json
import logging

log = logging.getLogger(__name__)

UTF8 = 'UTF-8'

BUF_DEFAULT = -1
BUF_UNBUFFERED = 0
BUF_LINEBUFFERED = 1


def messages(fp, key='@message'):
    """
    Read lines of UTF-8 from the file-like object given in ``fp``, with the
    same fault-tolerance as :function:`tagalog.io.lines`, but instead yield
    dicts with the line data stored in the key given by ``key`` (default:
    "@message").
    """
    for line in lines(fp):
        txt = line.rstrip('\n')
        yield {key: txt}


def json_messages(fp):
    """
    Similar to :function:`tagalog.io.messages` but input is already
    structured as JSON. Each event must be on a single line. Unparseable
    events will be skipped and raise a warning.
    """
    for line in lines(fp):
        try:
            item = json.loads(line)
        except ValueError as e:
            log.warn('Could not parse JSON message: {0}'.format(e))
            continue

        if not isinstance(item, dict) or not len(item) >= 1:
            log.warn('Skipping message not a dictionary of >=1 length')
            continue

        yield item


def lines(fp):
    """
    Read lines of UTF-8 from the file-like object given in ``fp``, making sure
    that when reading from STDIN, reads are at most line-buffered.

    UTF-8 decoding errors are handled silently. Invalid characters are
    replaced by U+FFFD REPLACEMENT CHARACTER.

    Line endings are normalised to newlines by Python's universal newlines
    feature.

    Returns an iterator yielding lines.
    """
    if fp.fileno() == sys.stdin.fileno():
        close = True

        try: # Python 3
            fp = open(fp.fileno(), mode='r', buffering=BUF_LINEBUFFERED, errors='replace')
            decode = False
        except TypeError:
            fp = os.fdopen(fp.fileno(), 'rU', BUF_LINEBUFFERED)
            decode = True

    else:
        close = False

        try:
            # only decode if the fp doesn't already have an encoding
            decode = (fp.encoding != UTF8)
        except AttributeError:
            # fp has been opened in binary mode
            decode = True

    try:
        while 1:
            l = fp.readline()
            if l:
                if decode:
                    l = l.decode(UTF8, 'replace')
                yield l
            else:
                break
    finally:
        if close:
            fp.close()

