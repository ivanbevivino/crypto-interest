import logging
import re

from flask import Flask, request, abort, current_app, jsonify
from werkzeug.utils import find_modules, import_string

from . import extensions
from . import models
from . import views



def create_app(environment=None):
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')
    app.logger.setLevel(logging.INFO)


    register_extensions(app)
    register_blueprints(app)
    # no more before_request (API Block) execution.

    return app


def register_extensions(app):
    extensions.db.init_app(app)


def register_blueprints(app):
    for module in find_modules('app.views'):
        app.register_blueprint(import_string(module).app)

