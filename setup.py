# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


with open('README.md') as readme:
    long_description = readme.read()

setup(
    name='deckard',
    description=(
        'A task runner, package builder, deploy tool'
    ),
    long_description=long_description,
    version='0.7',
    url='https://github.com/RoundingWellOS/deckard',
    author=u'Hernán Ciudad',
    author_email='hernan@roundingwell.com',
    packages=find_packages('.', exclude=['env']),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'deckard_queue_manager = deckard.queue:launch_queue_manager'
        ],
    },
    scripts=[
        'scripts/deckard.wsgi'
    ],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'boto==2.36.0',
        'click==3.3',
        'ecdsa==0.13',
        'Fabric==1.10.1',
        'Flask-SQLAlchemy==2.0',
        'Flask-WTF==0.11',
        'Flask==0.10.1',
        'GitHub-Flask==2.0.1',
        'github3.py==0.9.3',
        'itsdangerous==0.24',
        'Jinja2==2.7.3',
        'MarkupSafe==0.23',
        'paramiko==1.15.2',
        'psycopg2==2.6',
        'pycrypto==2.6.1',
        'requests==2.5.1',
        'SQLAlchemy==0.9.8',
        'uritemplate.py==0.3.0',
        'Werkzeug==0.10.1',
        'wsgiref==0.1.2',
        'WTForms==2.0.2'
    ]
)
