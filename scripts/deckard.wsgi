# -*- coding: utf-8 -*-
from deckard.http.app import app as application

import logging

if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=(
        application.config['LOGGING_LEVEL'] <= logging.DEBUG),
        port=application.config['HTTP_PORT'])
