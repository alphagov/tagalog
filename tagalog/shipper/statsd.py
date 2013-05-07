from socket import socket, AF_INET, SOCK_DGRAM
from socket import error as SocketError
import re
import logging

from tagalog.shipper.ishipper import IShipper

log = logging.getLogger(__name__)

class StatsdShipper(IShipper):
    def __init__(self,args,kwargs):
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.metric = kwargs['metric']
        host = kwargs.get('host','127.0.0.1')
        port = int(kwargs.get('port','8125'))
        self.statsd_addr = (host,port)

    def ship(self, msg):
        real_msg = self.__statsd_msg(msg).encode('utf-8')
        try:
            self.sock.sendto(real_msg, self.statsd_addr)
        except SocketError as e:
            log.warn("Could not ship message via StatsdShipper: {0}".format(e))

    def __statsd_msg(self, msg):
        pattern = r'%{([^}]*)}'
        replacement = lambda m: str(msg[m.group(1)])
        realised_metric = re.sub(pattern, replacement, self.metric)
        return realised_metric + ':1|c'
