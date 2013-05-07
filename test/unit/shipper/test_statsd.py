from mock import patch
from socket import socket

from tagalog.shipper.statsd import StatsdShipper

class TestStatsdShipper(object):
    @patch('tagalog.shipper.statsd.socket')
    def test_ship(self, socket_mock):
        ss = StatsdShipper(None,None)
        ss.ship({"@fields.status": 304,"@source_host":"wilmaaaaa"})

        socket_mock.return_value.sendto.assert_called_with('wilmaaaaa.304:1|c',('127.0.0.1',8125))
