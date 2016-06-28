from flask import request
from flask_restful import Api, Resource, abort

from cloudant.document import Document

from marshmallow import Schema, fields

from .db import get_db


class ScrapSchema(Schema):
    family = fields.Str(required=True)
    key = fields.Str(default=None)
    date = fields.DateTime(required=True)
    body = fields.Str(required=True)
    content_type = fields.Str(required=True)

scrap_schema = ScrapSchema()


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


def get_scraps_db():
    return get_db()['scraps']


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


def init_app(app):
    api = Api(app)
    api.add_resource(Root, '/')
    api.add_resource(ScrapCollection, '/scraps')
    # api.add_resource(ScrapItem, '/scraps/<scrapid>')
