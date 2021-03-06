from formencode import schema, validators
from formencode.variabledecode import variable_decode

from session import Session
from datastore import create_datastore

class AuthenticateSchema(schema.Schema):
    name=validators.UnicodeString(not_empty=True)
    password=validators.UnicodeString(not_empty=True)

class DatastoreSchema(schema.Schema):
    uri=validators.UnicodeString(if_missing=None, if_empty=None)
    database=validators.UnicodeString(if_missing=None, if_empty=None)
    authenticate=AuthenticateSchema(if_missing=None, if_empty=None)
    connect_retry=validators.Number(if_missing=3, if_empty=0)
    use_greenlets = validators.Bool(if_missing=False)
    # pymongo
    tz_aware=validators.Bool(if_missing=False)
    slave_okay=validators.Bool(if_missing=False)
    max_pool_size=validators.Int(if_missing=10)

def configure(**kwargs):
    """
    Given a (flat) dictionary of config values, creates DataStores
    and saves them by name
    """
    config = variable_decode(kwargs)
    configure_from_nested_dict(config['ming'])

def configure_from_nested_dict(config):
    datastores = {}
    for name, datastore in config.iteritems():
        args = DatastoreSchema.to_python(datastore, None)
        database = args.pop('database', None)
        if database is None:
            datastores[name] = create_datastore(**args)
        else:
            datastores[name] = create_datastore(database, **args)
    Session._datastores = datastores
    # bind any existing sessions
    for name, session in Session._registry.iteritems():
        session.bind = datastores.get(name, None)
        session._name = name
    
