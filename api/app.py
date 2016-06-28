import os
import json

from flask import Flask

from . import resources


def set_cloudfoundry_config(app):
    services_env = os.getenv('VCAP_SERVICES')
    assert services_env, 'Missing VCAP_SERVICES environment variable'
    services = json.loads(services_env)
    app.config['cf_services'] = services


app = Flask(__name__)
set_cloudfoundry_config(app)
resources.init_app(app)
