import re
import logging
import socket

from tagalog.shipper.ishipper import IShipper

log = logging.getLogger(__name__)

class StatsdShipper(IShipper):
    def __init__(self,args,kwargs):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.metric = kwargs['metric']
        host = kwargs.get('host','127.0.0.1')
        port = int(kwargs.get('port','8125'))
        self.sock.connect((host, port))

    def ship(self, msg):
        real_msg = self.__statsd_msg(msg).encode('utf-8')
        try:
            self.sock.send(real_msg)
        except socket.error as e:
            log.warn("Could not ship message via StatsdShipper: {0}".format(e))

    def __statsd_msg(self, msg):
        pattern = r'%{([^}]*)}'
        replacement = lambda m: str(msg[m.group(1)])
        realised_metric = re.sub(pattern, replacement, self.metric)
        return realised_metric + ':1|c'
