from tagalog.shipper.formatter import elasticsearch_bulk_decorate
from tagalog.shipper.ishipper import IShipper
import json

class StdoutShipper(IShipper):
    def __init__(self, args, kwargs):
        self.args = args
        self.key = kwargs.get('key','logs')
        self.bulk = kwargs.get('bulk',False)
        self.bulk_index = kwargs.get('bulk_index','logs')
        self.bulk_type = kwargs.get('bulk_type','message')


    def ship(self, msg):
        payload = json.dumps(msg)
        if self.bulk:
            payload = elasticsearch_bulk_decorate(self.bulk_index,self.bulk_type,payload)
        print(payload)
