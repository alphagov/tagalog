import json

def elasticsearch_bulk_decorate(bulk_index, bulk_type, msg):
    command = json.dumps({'index': {'_index': bulk_index, '_type': bulk_type}})
    return '{0}\n{1}\n'.format(command, msg)
