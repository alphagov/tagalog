from ...helpers import assert_raises
from mock import patch
import socket

from tagalog.shipper.statsd import StatsdShipper
from tagalog.shipper.shipper_error import ShipperError

class TestStatsdShipper(object):
    @patch('tagalog.shipper.statsd.socket.socket')
    def test_ship_with_provided_metric(self, socket_mock):
        kwargs = {'metric': '%{@source_host}.nginx.%{@fields.counter}'}
        ss = StatsdShipper(None, **kwargs)
        ss.ship({"@fields.counter": 'test', "@source_host":"wilmaaaaa", "@fields.randomness":"ignored"})

        socket_mock.return_value.connect.assert_called_with(('127.0.0.1', 8125))
        socket_mock.return_value.send.assert_called_with('wilmaaaaa.nginx.test:1|c'.encode('utf-8'))

    @patch('tagalog.shipper.statsd.socket.socket')
    def test_ship_with_provided_host_and_port(self, socket_mock):
        kwargs = {'metric': '%{@source_host}', 'host': 'statsd.cluster', 'port': '27623'}
        ss = StatsdShipper(None, **kwargs)
        ss.ship({"@source_host":"wilmaaaaa"})

        socket_mock.return_value.connect.assert_called_with(('statsd.cluster', 27623))
        socket_mock.return_value.send.assert_called_with('wilmaaaaa:1|c'.encode('utf-8'))

    @patch('tagalog.shipper.statsd.socket.socket')
    def test_ship_when_socket_error_occurs(self, socket_mock):
        kwargs = {'metric': '%{@source_host}', 'host': 'statsd.cluster', 'port': '27623'}
        ss = StatsdShipper(None, **kwargs)
        socket_mock.return_value.sendto.side_effect = socket.error('generic socket error')

        # should not raise
        ss.ship({"@source_host":"wilmaaaaa"})

    @patch('tagalog.shipper.statsd.socket.socket')
    def test_ship_when_host_name_is_incorrect(self, socket_mock):
        kwargs = {'metric': '%{@source_host}', 'host': 'statsd.cluster', 'port': '27623'}
        socket_mock.return_value.connect.side_effect = socket.gaierror('Thats not a host name!')

        # should raise
        assert_raises(socket.gaierror, StatsdShipper, None, **kwargs)

    @patch('tagalog.shipper.statsd.socket.socket')
    def test_ship_when_metric_not_provided(self, socket_mock):
        # should raise
        assert_raises(ShipperError, StatsdShipper, None)
