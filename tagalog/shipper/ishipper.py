import json

def elasticsearch_bulk_decorate(bulk_index, bulk_type, msg):
    command = json.dumps({'index': {'_index': bulk_index, '_type': bulk_type}})
    return '{0}\n{1}\n'.format(command, msg)


class IShipper(object):
    """
    Abstract class representing a log shipper. Log shippers should implement
    the following methods:
    """

    def __init__(self, args, kwargs):
        pass

    def ship(self, message):
        raise NotImplementedError('IShipper subclasses should implement the "ship" method!')
