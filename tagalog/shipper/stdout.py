from tagalog.shipper.ishipper import elasticsearch_bulk_decorate
from tagalog.shipper.ishipper import IShipper
import json

class StdoutShipper(IShipper):

    def ship(self, msg):
        payload = json.dumps(msg)
        if self.args.bulk:
            payload = elasticsearch_bulk_decorate(self.args.bulk_index,self.args.bulk_type,payload)
        print(payload)
