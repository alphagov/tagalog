from ...helpers import assert_true
from mock import patch, ANY
import re
import socket

from tagalog.shipper.statsd_timer import StatsdTimerShipper


class TestStatsdShipper(object):
    @patch('tagalog.shipper.statsd.socket.socket')
    def test_ship_with_provided_metric_literal(self, socket_mock):
        ss = StatsdTimerShipper(metric='%{@source_host}.nginx.foo', timed_field='request_time')
        ss.ship({"@source_host": 'wilmaaaaa', 'request_time': 32.25})

        socket_mock.return_value.connect.assert_called_with(('127.0.0.1', 8125))
        socket_mock.return_value.send.assert_called_with(ANY)
        args, kwargs = socket_mock.return_value.send.call_args
        packet = args[0]
        assert_true(re.search(r'^wilmaaaaa\.nginx\.foo:32\.250*\|ms$', packet.decode('utf-8')))
