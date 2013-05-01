from __future__ import print_function
import argparse
import csv
import json
import sys
import textwrap

from tagalog import io, filters

DEFAULT_FILTERS = 'init_txt,add_timestamp,add_source_host'

parser = argparse.ArgumentParser(description="Convert log data on STDIN to a "
                                             "stream of timestamped JSON "
                                             "documents on STDOUT.")
parser.add_argument('-f', '--filters', default=DEFAULT_FILTERS,
                    help='a list of filters to apply to each log line')
parser.add_argument('-a', '--filters-append', action='append',
                    help='A list of filters to apply to each log line '
                         '(appended to the default filter set)')


def main():
    args = parser.parse_args()
    filterlist = [args.filters]
    if args.filters_append:
        filterlist.extend(args.filters_append)
    pipeline = filters.build(','.join(filterlist))

    for msg in pipeline(io.lines(sys.stdin)):
        print(json.dumps(msg))


if __name__ == '__main__':
    main()
