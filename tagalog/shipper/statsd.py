from socket import socket, AF_INET, SOCK_DGRAM

from tagalog.shipper.ishipper import IShipper

class StatsdShipper(IShipper):
    def __init__(self,args,kwargs):
        self.sock = socket(AF_INET, SOCK_DGRAM)

    def ship(self, msg):
        statsd_msg = msg['@source_host'] + "." + str(msg["@fields.status"]) + ":1|c"
        self.sock.sendto(statsd_msg, ('127.0.0.1',8125))
