from ..helpers import *
import os
import redis
from tagalog.shipper import IShipper
from tagalog.shipper import RoundRobinConnectionPool
from tagalog.shipper import RedisShipper, StdoutShipper, NullShipper
from tagalog.shipper import register_shipper, unregister_shipper, get_shipper, build_shipper, parse_shipper


class MyShipper(IShipper):
    pass


class MockConnection(object):

    def __init__(self, **kwargs):
        self.pid = os.getpid()
        self.disconnected = 0
        for k, v in kwargs.items():
            setattr(self, k, v)

    def disconnect(self):
        self.disconnected += 1


class TestRoundRobinConnectionPool(object):

    def setup(self):
        self.p = RoundRobinConnectionPool(patterns=[{'name': 'a'},
                                                    {'name': 'b'}],
                                          connection_class=MockConnection)

    def test_get_connection(self):
        a = self.p.get_connection('SET')
        b = self.p.get_connection('SET')
        c = self.p.get_connection('SET')
        assert_equal(a.name, 'a')
        assert_equal(b.name, 'b')
        assert_equal(c.name, 'a')

    def test_add_pattern(self):
        a = self.p.get_connection('SET')
        self.p.add_pattern({'name': 'c'})
        b = self.p.get_connection('SET')
        c = self.p.get_connection('SET')
        assert_equal(a.name, 'a')
        assert_equal(b.name, 'b')
        assert_equal(c.name, 'c')

    def test_remove_pattern(self):
        self.p.remove_pattern({'name': 'a'})
        a = self.p.get_connection('SET')
        b = self.p.get_connection('SET')
        assert_equal(a.name, 'b')
        assert_equal(b.name, 'b')

    def test_remove_pattern_disconnects(self):
        a1 = self.p.get_connection('SET')
        b1 = self.p.get_connection('SET')
        self.p.remove_pattern({'name': 'a'})
        assert_equal(a1.disconnected, 1)

    def test_remove_pattern_during_cycle_new_conn(self):
        a1 = self.p.get_connection('SET')
        b1 = self.p.get_connection('SET')
        self.p.remove_pattern({'name': 'a'})
        b2 = self.p.get_connection('SET')
        assert_equal(b2.name, 'b')

    def test_remove_earlier_pattern_during_cycle(self):
        a1 = self.p.get_connection('SET')
        self.p.remove_pattern({'name': 'a'})
        b1 = self.p.get_connection('SET')
        assert_equal(b1.name, 'b')

    def test_remove_next_pattern_during_cycle(self):
        self.p.add_pattern({'name': 'c'})
        a1 = self.p.get_connection('SET')
        self.p.remove_pattern({'name': 'b'})
        c1 = self.p.get_connection('SET')
        assert_equal(c1.name, 'c')

    def test_remove_next_pattern_at_end_during_cycle(self):
        self.p.add_pattern({'name': 'c'})
        a1 = self.p.get_connection('SET')
        b1 = self.p.get_connection('SET')
        self.p.remove_pattern({'name': 'c'})
        a2 = self.p.get_connection('SET')
        assert_equal(a2.name, 'a')

    def test_remove_pattern_during_cycle_released_conn(self):
        a1 = self.p.get_connection('SET')
        b1 = self.p.get_connection('SET')
        self.p.remove_pattern({'name': 'a'})
        self.p.release(b1)
        b2 = self.p.get_connection('SET')
        assert_equal(b1, b2)

    def test_release(self):
        a1 = self.p.get_connection('SET')
        b1 = self.p.get_connection('SET')
        self.p.release(a1)
        self.p.release(b1)
        a2 = self.p.get_connection('SET')
        b2 = self.p.get_connection('SET')
        assert_equal(a1, a2)
        assert_equal(b1, b2)

    def test_purge_in_use(self):
        a1 = self.p.get_connection('SET')
        b1 = self.p.get_connection('SET')
        self.p.purge(a1)
        self.p.release(b1)
        a2 = self.p.get_connection('SET')
        b2 = self.p.get_connection('SET')
        assert_not_equal(a1, a2)
        assert_equal(b1, b2)
        assert_equal(a1.disconnected, 1)

    def test_purge_released(self):
        a1 = self.p.get_connection('SET')
        self.p.release(a1)
        self.p.purge(a1)
        self.p.get_connection('SET') # skip one
        a2 = self.p.get_connection('SET')
        assert_not_equal(a1, a2)
        assert_equal(a1.disconnected, 1)

    def test_disconnect(self):
        a1 = self.p.get_connection('SET')
        b1 = self.p.get_connection('SET')
        self.p.release(a1)
        self.p.release(b1)
        a2 = self.p.get_connection('SET')
        b2 = self.p.get_connection('SET')
        self.p.disconnect()
        assert_equal(a1.disconnected, 1)
        assert_equal(b1.disconnected, 1)
        assert_equal(a2.disconnected, 1)
        assert_equal(b2.disconnected, 1)

    def test_too_many_connections(self):
        p = RoundRobinConnectionPool(patterns=[{'name': 'a'},
                                               {'name': 'b'}],
                                     connection_class=MockConnection,
                                     max_connections_per_pattern=1)
        p.get_connection('SET')
        p.get_connection('SET')
        assert_raises(redis.ConnectionError, p.get_connection, 'SET')


class TestRedisShipper(object):

    def setup(self):
        self.args = MagicMock()
        self.args.urls = ["redis://foo", "redis://bar"]
        self.args.key = "logs"
        self.args.bulk = False

    @patch('tagalog.shipper.ResilientStrictRedis')
    def test_ship_catches_connection_errors(self, redis_mock):
        rs = RedisShipper(self.args)
        redis_mock.return_value.lpush.side_effect = redis.ConnectionError("Boom!")

        # should not raise:
        rs.ship("foo")

    @patch('tagalog.shipper.ResilientStrictRedis')
    def test_ship_catches_response_errors(self, redis_mock):
        rs = RedisShipper(self.args)
        redis_mock.return_value.lpush.side_effect = redis.ResponseError("Boom!")

        # should not raise:
        rs.ship("foo")

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

def test_build_redis_shipper():
    redis_shipper = build_shipper('redis')

    assert_true(isinstance(redis_shipper, RedisShipper))

def test_build_redis_shipper_with_key_arg():
    redis_shipper = build_shipper('redis,key=nginx-logs')

    assert_equal(redis_shipper.key, 'nginx-logs')

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
