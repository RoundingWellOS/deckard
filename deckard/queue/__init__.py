# -*- coding: utf-8 -*-
from .job_processor import JobProcessor

from deckard.config import settings
from deckard.db import db_session
from deckard.db.models import QueuedJob
from deckard.util.logger import Logger
from deckard.util.decorators import pidfile

import click
import logging
from sqlalchemy import select

import os
import time
import signal
import sys


class QueueManager(object):
    """
    QueueManager class, used to pluck jobs off the queue and process them,
    one at a time.
    """

    def __init__(self, log_level=logging.INFO):
        self._logger = Logger.get_logger('Queue Manager', to_screen=True)

    def _next_job(self):
        queued_job = QueuedJob.__table__

        select_job = select([queued_job.c.id]).\
            where(queued_job.c.status == QueuedJob.PENDING).\
            order_by(queued_job.c.created_ts.asc()).\
            limit(1).\
            with_for_update()

        update_job = queued_job.update().\
            returning(queued_job.c.id).\
            where(queued_job.c.id == select_job.as_scalar()).\
            values(status=QueuedJob.PROCESSING)

        res = db_session.execute(update_job).fetchone()
        if res:
            queued_job_id = res['id']
            db_session.commit()
            return JobProcessor(queued_job_id)
        else:
            db_session.rollback()

    def _handle_sigterm(self, signo, stackframe):
        self.stop()

    def _init_signal_handlers(self):
        signal.signal(signal.SIGTERM, self._handle_sigterm)

    def run(self):
        self._init_signal_handlers()
        self._logger.info("Deckard Queue Manager: Started on %s.", os.getpid())
        try:
            while True:
                job = self._next_job()

                if not job:
                    self._logger.debug(("No jobs. "
                                       "Sleeping for {} seconds").format(
                                           settings.Q_MGR_POLLING_INTERVAL))
                    time.sleep(settings.Q_MGR_POLLING_INTERVAL)
                    continue

                job.process()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self._logger.info("Deckard Queue Manager: Closing things down.")
        sys.exit(0)


@click.command()
@pidfile
def launch_queue_manager():
    queue_manager = QueueManager()
    queue_manager.run()

if __name__ == "__main__":
    launch_queue_manager()
