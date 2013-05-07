class IShipper(object):
    """
    Abstract class representing a log shipper. Log shippers should implement
    the following methods:
    """

    def ship(self, message):
        raise NotImplementedError('IShipper subclasses should implement the "ship" method!')
