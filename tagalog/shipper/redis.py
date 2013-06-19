from __future__ import absolute_import
import os
import json
import logging

from itertools import chain
from redis import Connection, ConnectionError, RedisError, StrictRedis

from tagalog.shipper.ishipper import IShipper
from tagalog.shipper.formatter import format_as_elasticsearch_bulk_json, format_as_json
from tagalog.shipper.shipper_error import ShipperError
from tagalog._compat import urlparse, _xrange


log = logging.getLogger(__name__)

class RoundRobinConnectionPool(object):
    """
    Round-robin Redis connection pool
    """
    def __init__(self,
                 patterns=None,
                 max_connections_per_pattern=None,
                 connection_class=Connection):
        self.patterns = []
        self.num_patterns = 0
        self.pid = os.getpid()
        self.connection_class = connection_class
        self.max_connections_per_pattern = max_connections_per_pattern or 2 ** 31
        self._pattern_idx = 0
        self._created_connections = []
        self._available_connections = []
        self._in_use_connections = []

        if patterns is not None:
            for patt in patterns:
                self.add_pattern(patt)

    def _checkpid(self):
        if self.pid != os.getpid():
            self.disconnect()
            self.__init__(self.patterns,
                          self.max_connections_per_pattern,
                          self.connection_class)

    def _next_pattern(self):
        self._pattern_idx = (self._pattern_idx + 1) % self.num_patterns

    def add_pattern(self, pattern):
        self.patterns.append(pattern)
        self.num_patterns += 1
        self._created_connections.append(0)
        self._available_connections.append([])
        self._in_use_connections.append(set())

    def remove_pattern(self, pattern):
        idx = self.patterns.index(pattern)
        self.patterns.pop(idx)

        # Keep the pattern index pointing at the correct pattern
        if idx < self._pattern_idx:
            self._pattern_idx -= 1

        # Disconnect connections for the removed pattern
        conns = chain(self._available_connections[idx],
                      self._in_use_connections[idx])
        for conn in conns:
            conn.disconnect()

        # Relabel all remaining connections
        for c in self.all_connections():
            if c._pattern_idx > idx:
                c._pattern_idx -= 1

        self._created_connections.pop(idx)
        self._available_connections.pop(idx)
        self._in_use_connections.pop(idx)
        self.num_patterns -= 1

        # Final adjustment to the pattern index to ensure we're not pointing
        # past the end of the pattern list
        if self._pattern_idx > self.num_patterns - 1:
            self._pattern_idx = 0

    def all_connections(self):
        """Returns a generator over all current connection objects"""
        for i in _xrange(self.num_patterns):
            for c in self._available_connections[i]:
                yield c
            for c in self._in_use_connections[i]:
                yield c

    def get_connection(self, command_name, *keys, **options):
        """Get a connection from the pool"""
        self._checkpid()
        try:
            connection = self._available_connections[self._pattern_idx].pop()
        except IndexError:
            connection = self.make_connection()
        self._in_use_connections[self._pattern_idx].add(connection)
        self._next_pattern()
        return connection

    def make_connection(self):
        """Create a new connection"""
        if self._created_connections[self._pattern_idx] >= self.max_connections_per_pattern:
            raise ConnectionError("Too many connections")
        self._created_connections[self._pattern_idx] += 1
        conn = self.connection_class(**self.patterns[self._pattern_idx])
        conn._pattern_idx = self._pattern_idx
        return conn

    def release(self, connection):
        """Releases the connection back to the pool"""
        self._checkpid()
        if connection.pid == self.pid:
            idx = connection._pattern_idx
            self._in_use_connections[idx].remove(connection)
            self._available_connections[idx].append(connection)

    def purge(self, connection):
        """Remove the connection from rotation"""
        self._checkpid()
        if connection.pid == self.pid:
            idx = connection._pattern_idx
            if connection in self._in_use_connections[idx]:
                self._in_use_connections[idx].remove(connection)
            else:
                self._available_connections[idx].remove(connection)
            connection.disconnect()

    def disconnect(self):
        """Disconnect all connections in the pool"""
        for conn in self.all_connections():
            conn.disconnect()

class ResilientStrictRedis(StrictRedis):

    @property
    def execution_attempts(self):
        if not hasattr(self, '_execution_attempts'):
            self._execution_attempts = 1
        return self._execution_attempts

    @execution_attempts.setter
    def execution_attempts(self, num):
        self._execution_attempts = num

    def execute_command(self, *args, **options):
        """Execute a command and return a parsed response"""
        pool = self.connection_pool
        command_name = args[0]
        for i in _xrange(self.execution_attempts):
            connection = pool.get_connection(command_name, **options)
            try:
                connection.send_command(*args)
                res = self.parse_response(connection, command_name, **options)
                pool.release(connection)
                return res

            # If anything goes wrong in .send_command() or .parse_response(),
            # and we don't catch it, this connection will never be returned to
            # the pool, and thus will leak.
            #
            # So, catch *everything* here except SystemExits and
            # KeyboardInterrupts.
            except Exception:
                pool.purge(connection)
                if i >= self.execution_attempts - 1:
                    raise


class RedisShipper(IShipper):

    def __init__(self, urls, key='logs', bulk=False, bulk_index='logs', bulk_type='message'):
        self.urls = urls
        self.key = key
        self.bulk = bulk
        self.bulk_index = bulk_index
        self.bulk_type = bulk_type

        patts = [self._parse_url(u) for u in self.urls]
        self.pool = RoundRobinConnectionPool(patterns=patts)
        self.rc = ResilientStrictRedis(connection_pool=self.pool)
        self.rc.execution_attempts = self.pool.num_patterns

    def ship(self, msg):
        if self.bulk:
            payload = format_as_elasticsearch_bulk_json(self.bulk_index,self.bulk_type,msg)
        else:
            payload = format_as_json(msg)
        try:
            self.rc.lpush(self.key, payload)
        except Exception as e:
            log.warn('Could not ship message: {0}'.format(e))

    def _parse_url(self, url):
        parsed = urlparse(url)
        db = 0

        if parsed.path.startswith('/'):
            path = parsed.path[1:]
        else:
            path = parsed.path

        if path:
            try:
                db = int(path)
            except ValueError:
                msg = 'Could not parse "{0}" as a valid Redis DB number!'.format(path)
                raise ValueError(msg)

        return {'host': parsed.hostname or 'localhost',
                'port': parsed.port or 6379,
                'db': db}



