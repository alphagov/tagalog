import re
import logging
import socket
import operator
from functools import reduce

from tagalog.shipper.ishipper import IShipper
from tagalog.shipper.shipper_error import ShipperError

log = logging.getLogger(__name__)

class StatsdShipper(IShipper):
    def __init__(self, metric, host='127.0.0.1', port='8125'):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.metric = metric
        portnum = int(port)
        self.sock.connect((host, portnum))

    def ship(self, msg):
        try:
            real_msg = self.__statsd_msg(msg).encode('utf-8')
            self.sock.send(real_msg)
        except socket.error as e:
            log.warn("Could not ship message via StatsdShipper: {0}".format(e))
        except KeyError as e:
            log.warn("Could not ship message via StatsdShipper: key {0} not found in message when constructing metric {1}".format(e,self.metric))

    def __statsd_msg(self, msg):
        def replace_metric_field(match):
            field = match.group(1)
            value = None
            if(field in msg):
                value = msg[field]
            else:
                pieces = field.split('.')
                # fetch from nested dict
                value = reduce(operator.getitem, pieces, msg)
            return str(value)

        pattern = r'%{([^}]*)}'
        realised_metric = re.sub(pattern, replace_metric_field, self.metric)
        return realised_metric + ':1|c'
