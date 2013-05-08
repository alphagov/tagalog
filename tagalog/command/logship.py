from __future__ import print_function, unicode_literals
import argparse
import json
import sys
import textwrap

from tagalog import io
from tagalog import filters
from tagalog.shipper import build_shipper

DEFAULT_FILTERS = 'init_txt,add_timestamp,add_source_host'

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent("""
    Ship log data from STDIN to somewhere else, timestamping and preprocessing
    each log entry into a JSON document along the way."""),
    epilog='''Parameter that various shipper accept
    stdout: bulk: whether to output in elasticsearch bulk format (default: false)
            bulk_index: elasticsearch index name (default: logs)
            bulk_type: adds elasticsearch _type in json (default: message)
    redis:  redis,url1,url2,....
            url1,url2,..urln: multiple redis servers you want to ship to
            bulk,bulk_index,bulk_type: as stdout shipper above
            key: redis list name (default: logs)
    statsd: metric: string value eg %{var1}.literal.%{var2}, where var1 and var2 would
                    be replaced with values from the message (required parameter)
            host: statsd host (default: 127.0.0.1)
            port: statsd port (default: 8125)''')
parser.add_argument('-f', '--filters', default=DEFAULT_FILTERS,
                    help='A list of filters to apply to each log line')
parser.add_argument('-a', '--filters-append', action='append',
                    help='A list of filters to apply to each log line '
                         '(appended to the default filter set)')
parser.add_argument('-s', '--shipper', nargs='+', default='redis,redis://localhost:6379',
                    help='''Select the shipper to be used to ship logs from redis, statsd, stdout and null.
                            You can specify multiple shippers using space as a delimiter. Also other arguments
                            can be passed to shipper separated by commas.
                            eg -s statsd,metric=%%{source}.nginx.%%{status},host=statsd.cluster,port=34532''')



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
