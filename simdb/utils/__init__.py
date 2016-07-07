from functools import wraps
import simdb
from mongoengine import connect
import mongoengine
import importlib
from pkg_resources import resource_filename as rs_fn
import ujson

from .. import odm_templates


def _ensure_connection(func):
    @wraps(func)
    def inner(*args, **kwargs):
        database = simdb.connection_config['database']
        host = simdb.connection_config['host']
        port = int(simdb.connection_config['port'])
        connect(db=database, host=host, port=port, alias=simdb.DATABASE_ALIAS)
        return func(*args, **kwargs)

    return inner


def db_disconnect():
    """Helper function to deal with stateful connections to mongoengine"""
    mongoengine.connection.disconnect(simdb.DATABASE_ALIAS)
    for collection in odm_templates.__all__:
        collection = getattr(odm_templates, collection)
        collection._collection = None


def db_connect(database, host, port):
    print('database = %s' % database)
    print('host = %s' % host)
    print('port = %s' % port)
    """Helper function to deal with stateful connections to mongoengine"""
    return connect(db=database, host=host, port=port,
                   alias=odm_templates.DATABASE_ALIAS)

SCHEMA_PATH = 'schemas'
SCHEMA_NAMES = {'calc': 'calc.json',
                'opt': 'opt.json',
                'pes': 'pes.json',
                'sim': 'sim.json'}
fn = '{}/{{}}'.format(SCHEMA_PATH)
schemas = {}
for name, filename in SCHEMA_NAMES.items():
    try:
        with open(rs_fn('simdb',
                        resource_name=fn.format(filename))) as fin:
            schemas[name] = ujson.load(fin)
    except IOError:
        raise Exception('Schema file not found or does not exist')
