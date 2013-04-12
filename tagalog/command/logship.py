from __future__ import print_function, unicode_literals
import argparse
import json
import sys
import textwrap

from tagalog import io, stamp, source_host, tag, fields
from tagalog import messages, json_messages
from tagalog import shipper

parser = argparse.ArgumentParser(description=textwrap.dedent("""
    Ship log data from STDIN to somewhere else, timestamping and preprocessing
    each log entry into a JSON document along the way."""))
parser.add_argument('-t', '--tags', nargs='+',
                    help='Tag each request with the specified string tags')
parser.add_argument('-f', '--fields', nargs='+',
                    help='Add key=value fields specified to each request')
parser.add_argument('-s', '--shipper', default='redis',
                    help='Select the shipper to be used to ship logs')
parser.add_argument('-j', '--json', action='store_true',
                    help='Content is already JSON')
parser.add_argument('--source-host', default=None,
                    help='Set the source host')
parser.add_argument('--no-stamp', action='store_true')
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

    lines = io.lines(sys.stdin)

    if args.json:
        msgs = json_messages(lines)
    else:
        msgs = messages(lines)

    msgs = source_host(msgs, args.source_host)

    if not args.no_stamp:
        msgs = stamp(msgs)
    if args.tags:
        msgs = tag(msgs, args.tags)
    if args.fields:
        msgs = fields(msgs, args.fields)
    for msg in msgs:
        payload = json.dumps(msg)
        if args.bulk:
            command = json.dumps({'index': {'_index': args.bulk_index, '_type': args.bulk_type}})
            payload = '{0}\n{1}\n'.format(command, payload)
        shpr.ship(payload)

if __name__ == '__main__':
    main()
