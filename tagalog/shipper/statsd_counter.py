from tagalog.shipper.statsd import StatsdShipper


class StatsdCounterShipper(StatsdShipper):
    def _statsd_msg(self, msg):
        return '1|c'
