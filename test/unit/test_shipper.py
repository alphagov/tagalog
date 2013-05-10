import os

from ..helpers import *
from tagalog.shipper.ishipper import IShipper
from tagalog.shipper.stdout import StdoutShipper
from tagalog.shipper import NullShipper
from tagalog.shipper import register_shipper, unregister_shipper, get_shipper, build_shipper, parse_shipper
from tagalog.shipper.redis import RedisShipper


class MyShipper(IShipper):
    pass


def test_shipper_registration():
    register_shipper('myshipper', MyShipper)
    assert_equal(get_shipper('myshipper'), MyShipper)
    unregister_shipper('myshipper')
    assert_equal(get_shipper('myshipper'), None)


def test_shipper_cant_reregister():
    register_shipper('myshipper', MyShipper)
    assert_raises(RuntimeError, register_shipper, 'myshipper', MyShipper)
    unregister_shipper('myshipper')


### method: build_shipper ###
def test_build_shipper():
    my_shipper = build_shipper('null')

    assert_true(isinstance(my_shipper, NullShipper))

def test_build_stdout_shipper():
    stdout_shipper = build_shipper('stdout')

    assert_true(isinstance(stdout_shipper, StdoutShipper))

def test_build_redis_shipper_with_key_arg():
    redis_shipper = build_shipper('redis,key=nginx-logs')

    assert_true(isinstance(redis_shipper, RedisShipper))
    assert_equal(redis_shipper.key, 'nginx-logs')

def test_build_redis_shipper_with_bulk_true():
    redis_shipper = build_shipper('redis,bulk=true')

    assert_true(isinstance(redis_shipper, RedisShipper))
    assert_true(redis_shipper.bulk)

def test_build_redis_shipper_with_bulk_false():
    redis_shipper = build_shipper('redis,bulk=false')

    assert_true(isinstance(redis_shipper, RedisShipper))
    assert_false(redis_shipper.bulk)

def test_build_redis_shipper_with_bulk_bogus():
    assert_raises(Exception, build_shipper,'redis,bulk=jobbies')

def test_build_stdout_shipper_with_bulk_true():
    shipper = build_shipper('stdout,bulk=true')

    assert_true(isinstance(shipper, StdoutShipper))
    assert_true(shipper.bulk)

def test_build_stdout_shipper_with_bulk_false():
    shipper = build_shipper('stdout,bulk=false')

    assert_true(isinstance(shipper, StdoutShipper))
    assert_false(shipper.bulk)


### method: parse_shipper
def test_parse_shipper():
    name, args, kwargs = parse_shipper('null')

    assert_equal(name, 'null')

def test_parse_shipper_with_kwarg():
    name, args, kwargs = parse_shipper('redis,key=nginx-logs')

    assert_equal(name, 'redis')
    assert_equal(kwargs, {'key':'nginx-logs'})

def test_parse_shipper_with_arg():
    name, args, kwargs = parse_shipper('redis,redis://localhost:8379')

    assert_equal(name, 'redis')
    assert_equal(args, ['redis://localhost:8379'])
