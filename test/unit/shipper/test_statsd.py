from mock import patch
import socket

from tagalog.shipper.statsd import StatsdShipper

class TestStatsdShipper(object):
    @patch('tagalog.shipper.statsd.socket')
    def test_ship_with_provided_metric(self, socket_mock):
        kwargs = {'metric': '%{@source_host}.nginx.%{@fields.counter}'}
        ss = StatsdShipper(None, kwargs)
        ss.ship({"@fields.counter": 'test', "@source_host":"wilmaaaaa", "@fields.randomness":"ignored"})

        socket_mock.return_value.sendto.assert_called_with('wilmaaaaa.nginx.test:1|c'.encode('utf-8'),
                ('127.0.0.1',8125))

    @patch('tagalog.shipper.statsd.socket')
    def test_ship_with_provided_host_and_port(self, socket_mock):
        kwargs = {'metric': '%{@source_host}', 'host': 'statsd.cluster', 'port': '27623'}
        ss = StatsdShipper(None, kwargs)
        ss.ship({"@source_host":"wilmaaaaa"})

        socket_mock.return_value.sendto.assert_called_with('wilmaaaaa:1|c'.encode('utf-8'),
                ('statsd.cluster',27623))

    @patch('tagalog.shipper.statsd.socket')
    def test_ship_when_socket_error_occurs(self, socket_mock):
        kwargs = {'metric': '%{@source_host}', 'host': 'statsd.cluster', 'port': '27623'}
        ss = StatsdShipper(None, kwargs)
        socket_mock.return_value.sendto.side_effect = socket.error('generic socket error')

        # should not raise
        ss.ship({"@source_host":"wilmaaaaa"})
