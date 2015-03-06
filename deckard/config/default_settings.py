# -*- coding: utf-8 -*-
import logging

# Development settings
DATABASE_URI = 'postgresql://deckard@localhost/deckard'
SECRET_KEY = 'development key'
LOGGING_LEVEL = logging.DEBUG
HTTP_PORT = 5000

GITHUB_CLIENT_ID = None
GITHUB_CLIENT_SECRET = None
GITHUB_ORG = None

# Fabric dependencies
SSH_CONFIG_PATH = None

# AWS S3 Bucket definitions (dummy credentials)
AWS_ACCESS_KEY_ID = 'AKIAXEWGERTDFGDFFDGF'
AWS_SECRET_ACCESS_KEY = 'Tm6B=R/B2xiLcKx9G[(66Gxrq#v4X6$tj3vSPYE('
S3_BUCKETS = {
    # Sample bucket definition
    # 'assets': {
    #     'name': 'my-s3-assets',
    #     'aws_access_key_id': AWS_ACCESS_KEY_ID,
    #     'aws_secret_access_key': AWS_SECRET_ACCESS_KEY
    # }
}

# Misc
LOGGING_SEPARATOR_PLACEHOLDER = '____SEPARATOR____'

# Queue manager
Q_MGR_POLLING_INTERVAL = 5
