import json

from tagalog.shipper.formatter import format_as_json, format_as_elasticsearch_bulk_json
from tagalog.shipper.ishipper import IShipper

class StdoutShipper(IShipper):
    def __init__(self, args, kwargs):
        self.args = args
        self.key = kwargs.get('key','logs')
        self.bulk = kwargs.get('bulk',False)
        self.bulk_index = kwargs.get('bulk_index','logs')
        self.bulk_type = kwargs.get('bulk_type','message')


    def ship(self, msg):
        if self.bulk:
            payload = format_as_elasticsearch_bulk_json(self.bulk_index,self.bulk_type,msg)
        else:
            payload = format_as_json(msg)
        print(payload)
