# -*- coding: utf-8 -*-
from .task_processor import TaskProcessor

from deckard.config import settings
from deckard.db import db_session
from deckard.db.models import QueuedJob
from deckard.util.logger import Logger

import datetime
import errno
import os
import shutil
import tempfile

import fabric.api as fabric_api
import fabric.network as fabric_network


class JobProcessor(object):
    """
    A wrapper around the QueuedJob db model to handle loading, verifying,
    and processing tasks.
    """

    def __init__(self, queued_job_id):

        self._db = QueuedJob.query.get(queued_job_id)
        self._logger = Logger.get_logger('Job {}'.format(queued_job_id),
                                         to_screen=True, queued_job=self._db)

        self._timestamp = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
        self._working_dir = tempfile.mkdtemp()
        self._context = dict(
            working_dir=self._working_dir,
            archive_path=self._archive_path,
            code_dir=self._code_dir,
            job_timestamp=self._timestamp,
            job=self._db.serialize()
        )

        self._db.tasks = self._db.job.tasks
        self._db.stages = self._db.job.stages
        db_session.commit()

        self._tasks = self._init_tasks(self._db.tasks)
        self._stages = self._db.stages

    def _log(self, *args):
        self._logger.info(*args, extra=dict(task=self.name))

    @property
    def name(self):
        return self.__class__.__name__.strip()

    @property
    def _archive_path(self):
        return os.path.join(self._working_dir, 'archive.tar')

    @property
    def _code_dir(self):
        return os.path.join(self._working_dir, self._timestamp)

    def _init_tasks(self, tasks):
        return [TaskProcessor(t, self._working_dir, self._db.stages,
                self._logger) for t in tasks]

    def _setup(self):
        fabric_api.env.parallel = True
        fabric_api.env.use_ssh_config = True
        if settings.SSH_CONFIG_PATH:
            fabric_api.env.ssh_config_path = settings.SSH_CONFIG_PATH

    def _download_archive(self):
        if self._db.git_fork:
            self._log("Downloading archive from GitHub")
            gc_client = self._db.user.github_client
            repo_owner, repo_name = self._db.git_fork.split('/')
            repo = gc_client.repository(repo_owner, repo_name)
            repo.archive('tarball', self._archive_path, self._db.git_ref)

            self._logger.debug("Downloading archive to {code_dir}".format(
                **self._context))

            self._log("Extracting archive")
            fabric_api.local('mkdir -p {code_dir}'.format(**self._context))
            with fabric_api.lcd(self._code_dir):
                fabric_api.local(
                    'tar --strip-components=1 -xf {archive_path}'.format(
                        **self._context))

    def _process_tasks(self):
        for i, task in enumerate(self._tasks):
            self._logger.separator()
            self._log("TASK %s: %s: %s", i + 1, task.name,
                      task.description)
            task.process(self._context)

    def _cleanup(self):
        try:
            fabric_network.disconnect_all()
            shutil.rmtree(self._working_dir)
        except OSError as ex:
            if ex.errno != errno.ENOENT:
                raise

    def _notify_rollbar(self):
            self._rollbar_token = os.environ.get('$ROLLBAR_TOKEN_SERVER')
            self._rollbar_environ = self._db.job.environment
            self._rollbar_revision = self._db.job.git_sha1
            self._rollbar_user = self._db.job.username
            self._rollbar_curl = "curl https://api.rollbar.com/api/1/deploy/ -F access_token="+self._rollbar_token+" -F environment="+self._rollbar_environ+" -F revision="+self._rollbar_revision+" -F local_username="+self._rollbar_username
            os.system(self._rollbar_curl)

    def process(self):
        try:
            self._setup()
            self._download_archive()
            self._process_tasks()
            self._notify_rollbar()
            self._db.mark_successful()
            self._logger.separator()
            self._log("Queued job %s is complete!", self._db.id)
        except Exception, ex:
            self._logger.exception(ex)
            self._db.mark_failed()
            raise
        finally:
            self._cleanup()
