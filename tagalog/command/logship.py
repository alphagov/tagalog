from __future__ import print_function, unicode_literals
import argparse
import json
import sys
import textwrap

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
parser.add_argument('--bulk', action='store_true',
                    help='Send log data in elasticsearch bulk format')
parser.add_argument('--bulk-index', default='logs',
                    help='Name of the elasticsearch index (default: logs)')
parser.add_argument('--bulk-type', default='message',
                    help='Name of the elasticsearch type (default: message)')

# TODO: make these the responsibility of the redis shipper
parser.add_argument('-k', '--key', default='logs')
parser.add_argument('-u', '--urls', nargs='+', default=['redis://localhost:6379'])

def main():
    args = parser.parse_args()
    shpr = shipper.get_shipper(args.shipper)(args)
    filterlist = [args.filters]
    if args.filters_append:
        filterlist.extend(args.filters_append)
    pipeline = filters.build(','.join(filterlist))

    for msg in pipeline(io.lines(sys.stdin)):
        shpr.ship(msg)

if __name__ == '__main__':
    main()
