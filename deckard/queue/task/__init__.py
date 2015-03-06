# -*- coding: utf-8 -*-
from deckard.config import settings

import boto
from fabric.api import cd, env, execute, lcd, local, put, sudo


class S3BucketNotConfigured(Exception):
    pass


class S3BucketInvalidConfiguration(Exception):
    pass


class TaskBase(object):
    """
    All Deckard job tasks must inherit from here in order to be processed.
    """

    _s3_buckets = None

    def __init__(self, working_directory, stages, logger):
        self._working_directory = working_directory
        self._stages = stages
        self._logger = logger

        self._s3_buckets = {}

    def _log(self, *args):
        self._logger.info(*args, extra=dict(task=self.name))

    @property
    def name(self):
        return self.__class__.__name__.strip()

    def _get_s3_bucket(self, key):
        if key not in self._s3_buckets:
            bucket_args = settings.S3_BUCKETS.get(key)

            if not bucket_args:
                raise S3BucketNotConfigured(
                    "No configuration provided for S3 bucket \"{}\"".format(
                        key))

            required_conf_keys = set(['name', 'aws_access_key_id',
                                     'aws_secret_access_key'])
            missing_conf_keys = required_conf_keys - set(bucket_args.keys())
            if missing_conf_keys:
                raise S3BucketInvalidConfiguration(
                    ("The S3 bucket \"{}\" is missing the following "
                        "configs: ").format(key, ", ".join(missing_conf_keys)))

            s3_conn = boto.connect_s3(
                aws_access_key_id=bucket_args['aws_access_key_id'],
                aws_secret_access_key=bucket_args['aws_secret_access_key'])
            self._s3_buckets[key] = s3_conn.get_bucket(bucket_args['name'])

        return self._s3_buckets[key]

    def process(self, context):
        raise NotImplementedError('Inheritors must implement'
                                  'the process method')

    def get_hosts_for_stage(self, name):
        return self._stages[name]

    def put(self, local_filename, remote_dir, remote_filename='.',
            stage=None, hosts=None):
        if stage and not hosts:
            hosts = self.get_hosts_for_stage(stage)

        def _put():
            with cd(remote_dir):
                inner_res = put(local_filename, remote_filename)

            return inner_res

        res = execute(_put, hosts=hosts)

        # TODO: Improve error handling
        # http://docs.fabfile.org/en/latest/usage/execution.html#intelligently-executing-tasks-with-execute

        return res

    def local_cmd(self, cmd, cwd=None):
        if not cwd:
            cwd = self._working_directory

        with lcd(cwd):
            res = local(cmd)

        # TODO: Improve error handling
        # http://docs.fabfile.org/en/latest/api/core/operations.html#fabric.operations.local

        return res

    def remote_cmd(self, cmd, cwd=None, stage=None, hosts=None):
        if stage and not hosts:
            hosts = self.get_hosts_for_stage(stage)

        if not cwd:
            cwd = '/tmp'

        def _cmd_remote():
            with cd(cwd):
                inner_res = sudo(cmd)

            return inner_res

        res = execute(_cmd_remote, hosts=hosts)

        # TODO: Improve error handling
        # http://docs.fabfile.org/en/latest/usage/execution.html#intelligently-executing-tasks-with-execute

        return res
