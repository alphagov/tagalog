import re
import logging
import socket
import operator
from functools import reduce

from tagalog.shipper.statsd import StatsdShipper
from tagalog.shipper.shipper_error import ShipperError

log = logging.getLogger(__name__)

class StatsdTimerShipper(StatsdShipper):
    def __init__(self, metric, timed_field, host='127.0.0.1', port='8125'):
        self.timed_field = timed_field
        super(StatsdTimerShipper, self).__init__(metric, host, port)

    def _statsd_msg(self, msg):
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
