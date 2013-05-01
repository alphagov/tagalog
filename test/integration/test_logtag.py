from ..helpers import assert_equal, assert_true
from subprocess import Popen, PIPE
import json


def test_defaults():
    p = Popen('logtag', shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input='hello'.encode("utf-8"))
    json_out = json.loads(data_out.decode("utf-8"))
    assert_equal('hello', json_out['@message'])
    assert_true('@timestamp' in json_out)
    assert_true('@source_host' in json_out)


def test_filters_append():
    p = Popen('logtag -a add_tags:handbags',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input='hello'.encode("utf-8"))
    json_out = json.loads(data_out.decode("utf-8"))
    assert_equal(['handbags'], json_out['@tags'])


def test_add_tags():
    p = Popen('logtag -f init_txt,add_tags:handbags',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input='hello'.encode("utf-8"))
    assert_equal({'@message': 'hello', '@tags': ['handbags']},
                 json.loads(data_out.decode("utf-8")))


def test_add_fields():
    p = Popen('logtag -f init_txt,add_fields:handbags=great',
              shell=True, stdout=PIPE, stdin=PIPE)
    data_out, _ = p.communicate(input='hello'.encode("utf-8"))
    assert_equal({'@message': 'hello', '@fields': { 'handbags': 'great'}},
                 json.loads(data_out.decode("utf-8")))
