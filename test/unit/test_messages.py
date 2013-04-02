from ..helpers import assert_equal
from tagalog import messages, json_messages


def test_messages():
    res = messages(['foo\n', 'bar\n', 'baz\n'])
    assert_equal(next(res), {'@message': 'foo'})
    assert_equal(next(res), {'@message': 'bar'})
    assert_equal(next(res), {'@message': 'baz'})


def test_messages_custom_key():
    res = messages(['foo\n', 'bar\n', 'baz\n'], key='msg')
    assert_equal(next(res), {'msg': 'foo'})
    assert_equal(next(res), {'msg': 'bar'})
    assert_equal(next(res), {'msg': 'baz'})


def test_json_messages():
    lines = [
      '{"@fields": {"text": "foo"}}\n',
      '{"@fields": {"text": "bar"}}\n',
      '{"@fields": {"text": "baz"}}\n',
    ]

    res = json_messages(lines)
    assert_equal(next(res), {'@fields': {'text': 'foo'}})
    assert_equal(next(res), {'@fields': {'text': 'bar'}})
    assert_equal(next(res), {'@fields': {'text': 'baz'}})


