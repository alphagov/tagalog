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
        return '1|c'
