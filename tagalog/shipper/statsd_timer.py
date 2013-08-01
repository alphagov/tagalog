import re
import logging
import socket
import operator
from functools import reduce

from tagalog.shipper.statsd import StatsdShipper, get_from_msg
from tagalog.shipper.shipper_error import ShipperError

log = logging.getLogger(__name__)

class StatsdTimerShipper(StatsdShipper):
    def __init__(self, metric, timed_field, host='127.0.0.1', port='8125'):
        self.timed_field = timed_field
        super(StatsdTimerShipper, self).__init__(metric, host, port)

    def _statsd_msg(self, msg):
        timed_value = get_from_msg(self.timed_field, msg)
        return '%f|ms' % timed_value
