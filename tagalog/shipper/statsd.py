from socket import socket, AF_INET, SOCK_DGRAM
import re

from tagalog.shipper.ishipper import IShipper

class StatsdShipper(IShipper):
    def __init__(self,args,kwargs):
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.metric = kwargs.get('metric', '%{@source_host}.%{@fields.status}')

    def ship(self, msg):
        real_msg = self.__statsd_msg(msg).encode('utf-8')
        self.sock.sendto(real_msg, ('127.0.0.1',8125))

    def __statsd_msg(self, msg):
        pattern = r'%{([^}]*)}'
        replacement = lambda m: str(msg[m.group(1)])
        realised_metric = re.sub(pattern, replacement, self.metric)
        return realised_metric + ':1|c'
