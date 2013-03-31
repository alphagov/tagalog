from ..helpers import assert_equal
import atexit
import os
import tempfile
from tagalog import io


def register_cleanup(fname):
    def _cleanup():
        os.remove(fname)
    atexit.register(_cleanup)


def test_lines():
    _, fname = tempfile.mkstemp()
    register_cleanup(fname)

    with open(fname, 'w') as f:
        f.writelines(['foo\n', 'bar\n', 'baz\n'])

    with open(fname) as f:
        res = io.lines(f)
        assert_equal(next(res), 'foo\n')
        assert_equal(next(res), 'bar\n')
        assert_equal(next(res), 'baz\n')


def test_messages():
    _, fname = tempfile.mkstemp()
    register_cleanup(fname)

    with open(fname, 'w') as f:
        f.writelines(['foo\n', 'bar\n', 'baz\n'])

    with open(fname) as f:
        res = io.messages(f)
        assert_equal(next(res), {'@message': 'foo'})
        assert_equal(next(res), {'@message': 'bar'})
        assert_equal(next(res), {'@message': 'baz'})


def test_messages_custom_key():
    _, fname = tempfile.mkstemp()
    register_cleanup(fname)

    with open(fname, 'w') as f:
        f.writelines(['foo\n', 'bar\n', 'baz\n'])

    with open(fname) as f:
        res = io.messages(f, key='msg')
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
        res = io.json_messages(f)
        assert_equal(next(res), {'@fields': {'text': 'foo'}})
        assert_equal(next(res), {'@fields': {'text': 'bar'}})
        assert_equal(next(res), {'@fields': {'text': 'baz'}})


def test_json_messages_unparseable():
    _, fname = tempfile.mkstemp()
    register_cleanup(fname)

    with open(fname, 'w') as f:
        f.writelines([
          '{"valid_json": 1}\n',
          'not valid json\n',
          '["not", "a", "dict"]\n',
          '{}\n',
          '{"valid_json": 2}\n',
        ])

    with open(fname) as f:
        res = io.json_messages(f)
        assert_equal(next(res), {'valid_json': 1})
        assert_equal(next(res), {'valid_json': 2})
