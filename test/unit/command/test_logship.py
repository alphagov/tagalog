from ...helpers import assert_true, assert_equal
from tagalog.command import logship
from tagalog.shipper import NullShipper, StdoutShipper, RedisShipper

### method: build_shipper ###
def test_build_shipper():
    my_shipper = logship.build_shipper('null')

    assert_true(isinstance(my_shipper, NullShipper))

def test_build_stdout_shipper():
    stdout_shipper = logship.build_shipper('stdout')

    assert_true(isinstance(stdout_shipper, StdoutShipper))

def test_build_redis_shipper():
    redis_shipper = logship.build_shipper('redis')

    assert_true(isinstance(redis_shipper, RedisShipper))

def test_build_redis_shipper_with_key_arg():
    redis_shipper = logship.build_shipper('redis,key=nginx-logs')

    assert_equal(redis_shipper.key, 'nginx-logs')

### method: parse_shipper
def test_parse_shipper():
    name, kwargs = logship.parse_shipper('null')

    assert_equal(name, 'null')

def test_parse_shipper_with_kwarg():
    name, kwargs = logship.parse_shipper('redis,key=nginx-logs')

    assert_equal(name, 'redis')
    assert_equal(kwargs, {'key':'nginx-logs'})
