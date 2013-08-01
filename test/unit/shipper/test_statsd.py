from ...helpers import assert_raises
from mock import patch
import socket

from tagalog.shipper.statsd import StatsdShipper
from tagalog.shipper.shipper_error import ShipperError


class DumbStatsdShipper(StatsdShipper):
    def _statsd_msg(self, msg):
        return "dumb|msg"

class TestStatsdShipper(object):
    @patch('tagalog.shipper.statsd.socket.socket')
    def test_ship_with_provided_metric_literal(self, socket_mock):
        ss = DumbStatsdShipper(metric='%{@source_host}.nginx.%{@fields.counter}')
        ss.ship({"@fields.counter": 'test', "@source_host":"wilmaaaaa"})

        socket_mock.return_value.connect.assert_called_with(('127.0.0.1', 8125))
        socket_mock.return_value.send.assert_called_with('wilmaaaaa.nginx.test:dumb|msg'.encode('utf-8'))

    @patch('tagalog.shipper.statsd.socket.socket')
    def test_ship_with_provided_metric_nested(self, socket_mock):
        ss = DumbStatsdShipper(metric='%{@source_host}.nginx.%{@fields.counter}')
        ss.ship({"@fields":{"counter": 'test',"randomness":"ignored"}, "@source_host":"wilmaaaaa"})

        socket_mock.return_value.connect.assert_called_with(('127.0.0.1', 8125))
        socket_mock.return_value.send.assert_called_with('wilmaaaaa.nginx.test:dumb|msg'.encode('utf-8'))

    @patch('tagalog.shipper.statsd.socket.socket')
    def test_ship_with_provided_metric_missing(self, socket_mock):
        ss = DumbStatsdShipper(metric='%{@source_host}.nginx.%{@fields.missing}')
        ss.ship({"@fields":{"counter": 'test',"randomness":"ignored"}, "@source_host":"wilmaaaaa"})

        socket_mock.return_value.connect.assert_called_with(('127.0.0.1', 8125))
        assert not socket_mock.return_value.send.called

    @patch('tagalog.shipper.statsd.socket.socket')
    def test_ship_with_provided_host_and_port(self, socket_mock):
        ss = DumbStatsdShipper(metric='%{@source_host}', host='statsd.cluster', port='27623')
        ss.ship({"@source_host":"wilmaaaaa"})

        socket_mock.return_value.connect.assert_called_with(('statsd.cluster', 27623))
        socket_mock.return_value.send.assert_called_with('wilmaaaaa:dumb|msg'.encode('utf-8'))

    @patch('tagalog.shipper.statsd.socket.socket')
    def test_ship_when_socket_error_occurs(self, socket_mock):
        ss = DumbStatsdShipper(metric='%{@source_host}', host='statsd.cluster', port='27623')
        socket_mock.return_value.sendto.side_effect = socket.error('generic socket error')

        # should not raise
        ss.ship({"@source_host":"wilmaaaaa"})

    @patch('tagalog.shipper.statsd.socket.socket')
    def test_ship_when_host_name_is_incorrect(self, socket_mock):
        socket_mock.return_value.connect.side_effect = socket.gaierror('Thats not a host name!')

        # should raise
        assert_raises(socket.gaierror, DumbStatsdShipper,
                      '%{@source_host}', 'statsd.cluster', '27623')
