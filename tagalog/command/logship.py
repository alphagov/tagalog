from __future__ import print_function, unicode_literals
import argparse
import json
import sys
import textwrap

from tagalog import io
from tagalog import filters
from tagalog.shipper import build_shipper

DEFAULT_FILTERS = 'init_txt,add_timestamp,add_source_host'

parser = argparse.ArgumentParser(description=textwrap.dedent("""
    Ship log data from STDIN to somewhere else, timestamping and preprocessing
    each log entry into a JSON document along the way."""))
parser.add_argument('-f', '--filters', default=DEFAULT_FILTERS,
                    help='A list of filters to apply to each log line')
parser.add_argument('-a', '--filters-append', action='append',
                    help='A list of filters to apply to each log line '
                         '(appended to the default filter set)')
parser.add_argument('-s', '--shipper', nargs='+', default='redis,redis://localhost:6379',
                    help='Select the shipper to be used to ship logs')

def main():
    args = parser.parse_args()

    shippers = []
    for shipper_desc in args.shipper:
        shippers.append(build_shipper(shipper_desc))

    filterlist = [args.filters]
    if args.filters_append:
        filterlist.extend(args.filters_append)
    pipeline = filters.build(','.join(filterlist))

    for msg in pipeline(io.lines(sys.stdin)):
        for shpr in shippers:
            shpr.ship(msg)

if __name__ == '__main__':
    main()
