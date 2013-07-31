import re
import logging
import socket
import operator
from functools import reduce

from tagalog.shipper.ishipper import IShipper
from tagalog.shipper.shipper_error import ShipperError

log = logging.getLogger(__name__)

class StatsdTimerShipper(IShipper):
    def __init__(self, metric, timed_field, host='127.0.0.1', port='8125'):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.metric = metric
        self.timed_field = timed_field
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
        def get_from_msg(field, msg):
            if(field in msg):
                return msg[field]
            else:
                pieces = field.split('.')
                # fetch from nested dict
                return reduce(operator.getitem, pieces, msg)

        def replace_metric_field(match):
            field = match.group(1)
            value = get_from_msg(field,msg)
            return str(value)

        pattern = r'%{([^}]*)}'
        realised_metric = re.sub(pattern, replace_metric_field, self.metric)
        timed_value = get_from_msg(self.timed_field, msg)
        return '%s:%f|ms' % (realised_metric, timed_value)
