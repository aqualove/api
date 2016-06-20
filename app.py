import os
import json

from flask import Flask, g, current_app, request
from flask_restful import Resource, Api, abort

from cloudant.client import Cloudant
from cloudant.document import Document

from marshmallow import Schema, fields


class ScrapSchema(Schema):
    family = fields.Str(required=True)
    key = fields.Str(default=None)
    date = fields.DateTime(required=True)
    body = fields.Str(required=True)
    content_type = fields.Str(required=True)

scrap_schema = ScrapSchema()


def make_store_connection():
    services = current_app.config['cf_services']
    creds = services['cloudantNoSQLDB'][0]['credentials']
    client = Cloudant(creds['username'], creds['password'], url=creds['url'])
    client.connect()
    return client


def get_store():
    store = getattr(g, '_store', None)
    if store is None:
        store = g._store = make_store_connection()
    return store


def get_scraps_db():
    store = get_store()
    scraps_db = store['scraps']
    return scraps_db


class Root(Resource):
    def get(self):
        links = [
            {'name': 'scraps', 'url': '/scraps'},
            ]
        return {'links': links}


def load_body(schema):
    json_data = request.get_json()
    if not json_data:
        abort(400, message='missing_arguments: No input data provided')
    data, errors = schema.load(json_data)
    if errors:
        abort(400, message='missing_arguments: %s' % errors)
    return data


class ScrapCollection(Resource):

    def get(self):
        db = get_scraps_db()
        items = list(db)
        return {'items': items}

    def post(self):
        body = load_body(scrap_schema)
        db = get_scraps_db()

        doc = Document(db)
        data = scrap_schema.dump(body).data

        body = data.pop('body')
        content_type = data.pop('content_type')

        doc.update(**data)
        doc.create()
        doc.put_attachment('body', content_type, body)
        return doc


def set_cloudfoundry_config(app):
    services_env = os.getenv('VCAP_SERVICES')
    assert services_env, 'Missing VCAP_SERVICES environment variable'
    services = json.loads(services_env)
    app.config['cf_services'] = services


def run(host='0.0.0.0', port=8080):
    app = Flask(__name__)
    set_cloudfoundry_config(app)
    api = Api(app)
    api.add_resource(Root, '/')
    api.add_resource(ScrapCollection, '/scraps')
    # api.add_resource(ScrapItem, '/scraps/<scrapid>')
    app.run(host=host, port=port)


if __name__ == '__main__':
    # On Bluemix, get the port number from the environment variable VCAP_APP_PORT
    # When running this app on the local machine, default the port to 8080
    port = int(os.getenv('VCAP_APP_PORT', 8080))
    run(port=port)
