from ...helpers import assert_raises
from mock import patch
import socket

from tagalog.shipper.statsd_counter import StatsdCounterShipper
from tagalog.shipper.shipper_error import ShipperError

class TestStatsdCounterShipper(object):
    @patch('tagalog.shipper.statsd.socket.socket')
    def test_ship_with_provided_metric_literal(self, socket_mock):
        kwargs = {'metric': '%{@source_host}.nginx.%{@fields.counter}'}
        ss = StatsdCounterShipper(**kwargs)
        ss.ship({"@fields.counter": 'test', "@source_host":"wilmaaaaa"})

        socket_mock.return_value.connect.assert_called_with(('127.0.0.1', 8125))
        socket_mock.return_value.send.assert_called_with('wilmaaaaa.nginx.test:1|c'.encode('utf-8'))

    @patch('tagalog.shipper.statsd.socket.socket')
    def test_ship_with_provided_metric_nested(self, socket_mock):
        kwargs = {'metric': '%{@source_host}.nginx.%{@fields.counter}'}
        ss = StatsdCounterShipper(**kwargs)
        ss.ship({"@fields":{"counter": 'test',"randomness":"ignored"}, "@source_host":"wilmaaaaa"})

        socket_mock.return_value.connect.assert_called_with(('127.0.0.1', 8125))
        socket_mock.return_value.send.assert_called_with('wilmaaaaa.nginx.test:1|c'.encode('utf-8'))

    @patch('tagalog.shipper.statsd.socket.socket')
    def test_ship_with_provided_metric_missing(self, socket_mock):
        kwargs = {'metric': '%{@source_host}.nginx.%{@fields.missing}'}
        ss = StatsdCounterShipper(**kwargs)
        ss.ship({"@fields":{"counter": 'test',"randomness":"ignored"}, "@source_host":"wilmaaaaa"})

        socket_mock.return_value.connect.assert_called_with(('127.0.0.1', 8125))
        assert not socket_mock.return_value.send.called
