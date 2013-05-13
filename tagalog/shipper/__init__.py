import csv

from tagalog.shipper.redis import RedisShipper
from tagalog.shipper.stdout import StdoutShipper
from tagalog.shipper.statsd import StatsdShipper
from tagalog.shipper.ishipper import IShipper


SHIPPERS = {}


class NullShipper(IShipper):
    def __init__(self):
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


def str2bool(s):
    mapping = {'true': True,'false': False}
    return mapping[s]


def build_redis(*args, **kwargs):
    if 'bulk' in kwargs:
        kwargs['bulk'] = str2bool(kwargs['bulk'])
    return RedisShipper(urls=args,**kwargs)


def build_stdout(*args, **kwargs):
    if 'bulk' in kwargs:
        kwargs['bulk'] = str2bool(kwargs['bulk'])
    if args:
        raise ShipperError("unexpected positional arguments to stdout shipper")
    return StdoutShipper(**kwargs)


def build_statsd(*args, **kwargs):
    if args:
        raise ShipperError("unexpected positional arguments to statsd shipper")
    return StatsdShipper(**kwargs)


def build_null(*args, **kwargs):
    return NullShipper()


register_shipper('redis', build_redis)
register_shipper('stdout', build_stdout)
register_shipper('statsd', build_statsd)
register_shipper('null', build_null)


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

    return get_shipper(name)(*ship_args, **kwargs)
