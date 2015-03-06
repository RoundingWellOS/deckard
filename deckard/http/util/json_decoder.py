# -*- coding: utf-8 -*-
from datetime import datetime
from flask.json import JSONEncoder


class CustomJSONEncoder(JSONEncoder):

    def default(self, o):
        try:
            if isinstance(o, datetime):
                return o.strftime('%Y-%m-%dT%H:%M:%S%z')
            iterable = iter(o)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, o)
