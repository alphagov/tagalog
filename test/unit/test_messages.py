from ..helpers import assert_equal
import atexit
import os
import tempfile
from tagalog import messages, json_messages


def register_cleanup(fname):
    def _cleanup():
        os.remove(fname)
    atexit.register(_cleanup)


def test_messages():
    _, fname = tempfile.mkstemp()
    register_cleanup(fname)

    with open(fname, 'w') as f:
        f.writelines(['foo\n', 'bar\n', 'baz\n'])

    with open(fname) as f:
        res = messages(f)
        assert_equal(next(res), {'@message': 'foo'})
        assert_equal(next(res), {'@message': 'bar'})
        assert_equal(next(res), {'@message': 'baz'})


def test_messages_custom_key():
    _, fname = tempfile.mkstemp()
    register_cleanup(fname)

    with open(fname, 'w') as f:
        f.writelines(['foo\n', 'bar\n', 'baz\n'])

    with open(fname) as f:
        res = messages(f, key='msg')
        assert_equal(next(res), {'msg': 'foo'})
        assert_equal(next(res), {'msg': 'bar'})
        assert_equal(next(res), {'msg': 'baz'})


def test_json_messages():
    _, fname = tempfile.mkstemp()
    register_cleanup(fname)

    with open(fname, 'w') as f:
        f.writelines([
          '{"@fields": {"text": "foo"}}\n',
          '{"@fields": {"text": "bar"}}\n',
          '{"@fields": {"text": "baz"}}\n',
        ])

    with open(fname) as f:
        res = json_messages(f)
        assert_equal(next(res), {'@fields': {'text': 'foo'}})
        assert_equal(next(res), {'@fields': {'text': 'bar'}})
        assert_equal(next(res), {'@fields': {'text': 'baz'}})


def test_json_messages_unparseable():
    _, fname = tempfile.mkstemp()
    register_cleanup(fname)

