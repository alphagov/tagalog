from socket import socket, AF_INET, SOCK_DGRAM
import re

from tagalog.shipper.ishipper import IShipper

class StatsdShipper(IShipper):
    def __init__(self,args,kwargs):
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.metric = kwargs['metric']
        host = kwargs.get('host','127.0.0.1')
        port = int(kwargs.get('port','8125'))
        self.statsd_addr = (host,port)

    def ship(self, msg):
        real_msg = self.__statsd_msg(msg).encode('utf-8')
        self.sock.sendto(real_msg, self.statsd_addr)

    def __statsd_msg(self, msg):
        pattern = r'%{([^}]*)}'
        replacement = lambda m: str(msg[m.group(1)])
        realised_metric = re.sub(pattern, replacement, self.metric)
        return realised_metric + ':1|c'
