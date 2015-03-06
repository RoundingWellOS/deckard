# -*- coding: utf-8 -*-
from deckard.http.app import github

from flask import request, session
from functools import wraps


def login_required(func):
    @wraps(func)
    def _decorator(*args, **kwargs):
        if session.get('user_id', None) is None:
            session['post_auth_redirect'] = request.path
            return github.authorize(scope='user,repo,read:org')
        return func(*args, **kwargs)
    return _decorator
