# -*- coding: utf-8 -*-
from deckard.db import db_session, init_db
from deckard.db.models import User
from deckard.http.util.json_decoder import CustomJSONEncoder

import logging

from flask import Flask, g, session
from flask.ext.github import GitHub
from flask_wtf.csrf import CsrfProtect

csrf = CsrfProtect()

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder
app.config.from_object('deckard.config.settings')

csrf.init_app(app)

# setup github-flask
github = GitHub(app)

from deckard.http.controllers.core import *
from deckard.http.controllers.job import *
from deckard.http.controllers.user import *


@csrf.error_handler
def csrf_error(reason):
    return jsonify(data=reason, _status=False), 403


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@app.after_request
def after_request(response):
    db_session.remove()
    return response


@github.access_token_getter
def token_getter():
    user = g.user
    if user is not None:
        return user.github_access_token


def deckard_wsgi_app():
    app.run(host='0.0.0.0', debug=(
        app.config['LOGGING_LEVEL'] <= logging.DEBUG),
        port=app.config['HTTP_PORT'])


if __name__ == '__main__':
    init_db()
    deckard_wsgi_app()
