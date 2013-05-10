import json

from tagalog.shipper.formatter import format_as_json, format_as_elasticsearch_bulk_json
from tagalog.shipper.ishipper import IShipper

class StdoutShipper(IShipper):
    def __init__(self, bulk=False, bulk_index='logs', bulk_type='message'):
        self.bulk = bulk
        self.bulk_index = bulk_index
        self.bulk_type = bulk_type


    def ship(self, msg):
        if self.bulk:
            payload = format_as_elasticsearch_bulk_json(self.bulk_index,self.bulk_type,msg)
        else:
            payload = format_as_json(msg)
        print(payload)
