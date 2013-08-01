import re
import logging
import socket
import operator
from functools import reduce

from tagalog.shipper.statsd import StatsdShipper
from tagalog.shipper.shipper_error import ShipperError

log = logging.getLogger(__name__)

class StatsdCounterShipper(StatsdShipper):
    def _statsd_msg(self, msg):
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
