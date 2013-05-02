from __future__ import print_function, unicode_literals
import argparse
import json
import sys
import textwrap
import csv

from tagalog import io
from tagalog import filters
from tagalog import shipper

DEFAULT_FILTERS = 'init_txt,add_timestamp,add_source_host'

parser = argparse.ArgumentParser(description=textwrap.dedent("""
    Ship log data from STDIN to somewhere else, timestamping and preprocessing
    each log entry into a JSON document along the way."""))
parser.add_argument('-f', '--filters', default=DEFAULT_FILTERS,
                    help='A list of filters to apply to each log line')
parser.add_argument('-a', '--filters-append', action='append',
                    help='A list of filters to apply to each log line '
                         '(appended to the default filter set)')
parser.add_argument('-s', '--shipper', default='redis',
                    help='Select the shipper to be used to ship logs')


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
    """TODO: write"""
    from argparse import Namespace
    args = Namespace()
    args.key = 'logs'
    args.bulk = False
    args.bulk_index = 'logs'
    args.bulk_type = 'message'

    name, ship_args, kwargs = parse_shipper(description)
    if 'key' in kwargs:
        args.key = kwargs['key']
    if 'bulk' in kwargs:
        args.bulk = kwargs['bulk']
    if 'bulk_index' in kwargs:
        args.bulk_index = kwargs['bulk_index']
    if 'bulk_type' in kwargs:
        args.bulk_type = kwargs['bulk_type']
    args.urls = ship_args

    return shipper.get_shipper(name)(args)

def main():
    args = parser.parse_args()

    shpr = build_shipper(args.shipper)

    filterlist = [args.filters]
    if args.filters_append:
        filterlist.extend(args.filters_append)
    pipeline = filters.build(','.join(filterlist))

    for msg in pipeline(io.lines(sys.stdin)):
        shpr.ship(msg)

if __name__ == '__main__':
    main()
