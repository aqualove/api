from flask import g, current_app

from cloudant.client import Cloudant


def make_db_connection():
    services = current_app.config['cf_services']
    creds = services['cloudantNoSQLDB'][0]['credentials']
    client = Cloudant(creds['username'], creds['password'], url=creds['url'])
    client.connect()
    return client


def get_db():
    db = getattr(g, '_db', None)
    if db is None:
        db = g._db = make_db_connection()
    return db
