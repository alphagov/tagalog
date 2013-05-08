import re
import logging
import socket

from tagalog.shipper.ishipper import IShipper
from tagalog.shipper.shipper_error import ShipperError

log = logging.getLogger(__name__)

class StatsdShipper(IShipper):
    def __init__(self, args, metric=None, host='127.0.0.1', port='8125'):
        if metric == None:
            raise ShipperError("statsd shipper must be specified with the metric parameter")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.metric = metric
        portnum = int(port)
        self.sock.connect((host, portnum))

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
