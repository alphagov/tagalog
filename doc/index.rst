Tagalog: simple tools for manipulating logging data
===================================================

Welcome. This is the documentation for Tagalog_, a set of simple tools for the
command line which aim to help system operators manage line-oriented logging
data. Tagalog includes tools that

.. _Tagalog: https://github.com/alphagov/tagalog/

- tag each log line with an accurate timestamp
- convert log lines into Logstash_-compatible JSON documents
- ship log lines over the network for further processing
- compute statistics over log streams by sending data to Statsd_

.. _Logstash: http://logstash.net/
.. _Statsd: https://github.com/etsy/statsd/

This document aims to give a general introduction to Tagalog.

Documentation index
-------------------

.. toctree::
   :maxdepth: 4

   Introduction <self>
   commands
   tagalog

Why would I use Tagalog?
------------------------

If you are managing a large infrastructure, you're probably generating a lot of
log data. It's becoming common practice to send this data to a central location
(an elasticsearch_ cluster, typically) for further analysis (perhaps using
Kibana_). At the Government Digital Service, we use Tagalog to tag, parse, and
ship our logging data to a set of Redis_ servers, out of which it is then
fetched by an elasticsearch cluster using the `elasticsearch redis river`_.

There are other tools which do similar things, such as Logstash_ and, in
particular, lumberjack_. If Tagalog doesn't suit your needs, perhaps one of
these will.

.. _elasticsearch: http://www.elasticsearch.org/
.. _Kibana: http://kibana.org/
.. _Redis: http://redis.io/
.. _elasticsearch redis river: https://github.com/leeadkins/elasticsearch-redis-river
.. _lumberjack: https://github.com/jordansissel/lumberjack

What is logging data?
---------------------

Most programs generate some kind of logging data. Your webserver generates
access and error logs, while applications and system daemons will inform you of
warnings and errors in their logs. Tagalog is broadly agnostic about what you
log, but it will work best if each line of logging data can be considered a
distinct, timestamped event. While Tagalog won't prevent you using multi-line
log formats, it's generally much harder to search and analyse them, so we
suggest that if possible, you try and use single-line log entries, ideally in a
format that's both human-readable and machine-parseable, such as the `Lograge
format`_.


What does Tagalog do?
---------------------

Tagalog isn't a single tool. Rather, it's a set of tools which are designed to
work together. Two of the more important ones are ``logtag`` and ``logship``,
and they both treat logging data in a similar manner. They both expect lines of
logging data on their standard input [#]_, and then apply a series of filters to
those log lines. Each of these filters typically performs quite a small task:
examples include:

- ``init_txt``: transforms a line of UTF-8 text into a JSON document with the
  message contents in a field named ``@message``. This is typically the first
  filter applied.

- ``add_timestamp``: adds a precise timestamp to a JSON document in a field
  named ``@timestamp``.

- ``add_tags``: adds user specified tags to an array in a field named ``@tags``.

- ``parse_lograge``: tries to parse any ``key=value`` pairs (`Lograge format`_)
  in the ``@message`` field and adds them to a JSON document in a field named
  ``@fields``.

``logtag`` and ``logship`` both accept arguments that allow you to build a
"filter chain": a series of filters which are applied to the incoming log data.
At the end of the filter chain, ``logtag`` prints the results to its standard
output, while ``logship`` (with some additional configuration) ships the log
data across the network for further processing.

.. _Lograge format: https://github.com/roidrage/lograge

.. [#] Support for logging directly from files (log tailing) is being considered
       for a future release.

Tagalog commands
----------------

The next step to using Tagalog is to introduce yourself to the :ref:`commands`.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
