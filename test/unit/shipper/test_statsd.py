from mock import patch
from socket import socket

from tagalog.shipper.statsd import StatsdShipper

class TestStatsdShipper(object):
    @patch('tagalog.shipper.statsd.socket')
    def test_ship(self, socket_mock):
        ss = StatsdShipper(None, {})
        ss.ship({"@fields.status": 304, "@source_host":"wilmaaaaa"})

        socket_mock.return_value.sendto.assert_called_with('wilmaaaaa.304:1|c'.encode('utf-8'), ('127.0.0.1',8125))

    @patch('tagalog.shipper.statsd.socket')
    def test_ship_with_provided_metric(self, socket_mock):
        kwargs = {'metric': '%{@source_host}.%{@fields.counter}'}
        ss = StatsdShipper(None, kwargs)
        ss.ship({"@fields.counter": 'test', "@source_host":"wilmaaaaa", "@fields.randomness":"ignored"})

        socket_mock.return_value.sendto.assert_called_with('wilmaaaaa.test:1|c'.encode('utf-8'), ('127.0.0.1',8125))
