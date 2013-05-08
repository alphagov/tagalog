import csv

from tagalog.shipper.redis import RedisShipper
from tagalog.shipper.stdout import StdoutShipper
from tagalog.shipper.statsd import StatsdShipper
from tagalog.shipper.ishipper import IShipper


SHIPPERS = {}


class NullShipper(IShipper):
    def __init__(self, args):
        pass

    def ship(self, msg):
        pass


def register_shipper(name, constructor):
    if name not in SHIPPERS:
        SHIPPERS[name] = constructor
    else:
        raise RuntimeError('Shipper "{0}" already defined!'.format(name))


def unregister_shipper(name):
    return SHIPPERS.pop(name, None)


def get_shipper(name):
    return SHIPPERS.get(name)

register_shipper('redis', RedisShipper)
register_shipper('stdout', StdoutShipper)
register_shipper('statsd', StatsdShipper)
register_shipper('null', NullShipper)


def parse_shipper(description):
    clauses = next(csv.reader([description])) #reading only a single line
    kwargs = {}
    args = []
    for clause in clauses[1:]:
        if '=' in clause:
            key, val = clause.split("=")
            kwargs[key] = val
        else:
            args.append(clause)
    return clauses[0], args, kwargs

def build_shipper(description):
    """Takes a command-line description of a shipper and build the relevant shipper from it"""

    name, ship_args, kwargs = parse_shipper(description)

    return get_shipper(name)(ship_args, **kwargs)
