.. _commands:

Tagalog commands
================

The following page documents the Tagalog command-line utilities.

``logtag``
----------

``logtag`` accepts lines of log input on STDIN, applies a filter chain to the
log data, and then prints the resulting log entries to STDOUT.

By default, ``logtag`` has a filter chain of
``init_txt,add_timestamp,add_source_host``. This means that it will treat
incoming log data as plain text, and will add a timestamp and hostname data to
the log entries.

To use ``logtag`` in its default configuration, simply pass data on STDIN,
calling ``logtag`` without arguments::

    $ program_to_log | logtag
    {"@timestamp": "2013-05-10T16:06:53.441811Z", "@source_host": "lynx.local", "@message": "my log entry"}
    {"@timestamp": "2013-05-10T16:06:53.442090Z", "@source_host": "lynx.local", "@message": "another one"}

To tag each log entry with "foo" and parse Lograge format logs into the
``@fields`` field::

    $ program_to_log | logtag --filters-append add_tags:foo,parse_lograge
    {"@timestamp": "2013-05-10T16:08:26.999239Z", ..., "@message": "a log with=some key=value pairs", "@tags": ["foo"], "@fields": {"with": "some", "key": "value"}}
    {"@timestamp": "2013-05-10T16:08:26.999505Z", ..., "@message": "another=one", "@tags": ["foo"], "@fields": {"another": "one"}}

If your program emits JSON objects, you might want to use a different filter
chain that parses the incoming data as JSON::

    $ program_emitting_json | logtag --filters init_json,add_timestamp
    {"age": 67, "name": "Bob Dole", "@timestamp": "2013-05-10T16:13:49.558039Z"}
    {"age": 43, "name": "John Doe", "@timestamp": "2013-05-10T16:13:49.558452Z"}

``logship``
-----------

``logship`` works just like ``logtag``, but instead of printing the results to
STDOUT, it ships the resulting log entries to one or more "shippers." Shippers
include:

- ``redis``: a shipper that pushes log entries onto a Redis_ list.
- ``statsd``: a shipper that submits data to Statsd_ on the basis of log
  contents.
- ``stdout``: a shipper that simply prints to STDOUT. Mainly used for debugging.

.. _Redis: http://redis.io
.. _Statsd: https://github.com/etsy/statsd/

To ship log data to a Redis server, you might invoke ``logship`` as follows::

    $ program_to_log | logship --shipper redis,redis://localhost:6379

You can configure filters with the ``--filters-append`` and ``--filters``
options, just as you can with ``logtag``::

    $ program_emitting_json | logship --filters init_json,add_timestamp --shipper redis,redis://localhost:6379

The Redis shipper can take multiple server addresses. It will round-robin
between the list of servers. If one server is down, or out-of-memory, or
otherwise unable to accept log entries, ``logship`` will attempt to submit the
log entry to one of the other servers.

::

    $ program_to_log | logship --shipper redis,redis://redis-1.local:6379,redis://redis-2.local:6379

For further shipper documentation, see the API documentation for the
:mod:`tagalog.shipper` package and its submodules (e.g.
:mod:`tagalog.shipper.redis`, :mod:`tagalog.shipper.statsd`).

``logtext``
-----------

``logtext`` accepts a stream of newline-delimited Logstash-format JSON documents
on STDIN, and prints the log messages on STDOUT. If the log entries have a
timestamp, the lines will be prefixed with the timestamp::

    $ echo '{"@message":"hello"}\n{"@message":"world"}' | logtext
    hello
    world

``logstamp``
------------

``logstamp`` accepts lines of input on STDIN, and emits each line prefixed with
a high-precision ISO8601 timestamp on STDOUT::

    $ echo "hello\nworld" | logstamp
    2013-05-13T08:59:50.750691Z hello
    2013-05-13T08:59:50.751132Z world
