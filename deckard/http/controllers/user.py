# -*- coding: utf-8 -*-
from deckard.db.models import User
from deckard.http.app import app
from deckard.http.util.decorators import login_required

from flask import jsonify, render_template, session


@app.route('/user')
@login_required
def user():
    user = User.query.get(session.get('user_id'))
    return jsonify(data=user.serialize())


@app.route('/unauthorized')
def unauthorized():
    return render_template(u'unauthorized.html')
