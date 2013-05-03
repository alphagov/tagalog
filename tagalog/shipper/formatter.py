import json


def elasticsearch_bulk_decorate(bulk_index, bulk_type, msg):
    """ Decorates the msg with elasticsearch bulk format and adds index and message type"""
    command = json.dumps({'index': {'_index': bulk_index, '_type': bulk_type}})
    return '{0}\n{1}\n'.format(command, msg)

def format_as_json(msg):
    return json.dumps(msg)

def format_as_elasticsearch_bulk_json(bulk_index, bulk_type, msg):
    payload = format_as_json(msg)
    return elasticsearch_bulk_decorate(bulk_index, bulk_type, payload)
