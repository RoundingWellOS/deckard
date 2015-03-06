# -*- coding: utf-8 -*-
from deckard.config import settings
from deckard.db import db_session
from deckard.db.models import User
from deckard.http.app import app, github
from deckard.http.util.decorators import login_required

from flask import render_template, request, session, redirect, url_for


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/github-callback')
@github.authorized_handler
def authorized(access_token):
    next_url = request.args.get('next') or url_for('home')
    post_auth_redirect = session.pop('post_auth_redirect',
                                     url_for('job_enqueue'))

    if access_token is None:
        return redirect(next_url)

    params = {'access_token': access_token}

    gh_user = github.get('user', params=params)
    github_login = gh_user['login']

    if settings.GITHUB_ORG:
        res = github.raw_request('GET', 'orgs/{0}/members/{1}'.format(
            settings.GITHUB_ORG, github_login), params=params)
        if res.status_code != 204:
            session.pop('user_id', None)
            return redirect(url_for('unauthorized'))

    user = User.query.filter_by(github_login=github_login).first()
    if user is None:
        user = User(github_login=github_login)
        db_session.add(user)
    user.github_name = gh_user.get('name')
    user.github_avatar = gh_user.get('avatar_url')
    user.github_access_token = access_token
    db_session.commit()

    session['user_id'] = user.id
    return redirect(post_auth_redirect)


@app.route('/login')
@login_required
def login():
    return redirect(url_for('job_enqueue'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))
