# -*- coding: utf-8 -*-
from deckard.config import settings
from deckard.db import db_session

import logging
from logging import StreamHandler
from logging.handlers import SysLogHandler
import platform
import sys
import types


def log_separator(self):
    # Remove standard loggers
    if hasattr(self, 'sys_logger'):
        self.removeHandler(self.sys_logger)
    if hasattr(self, 'screen_logger'):
        self.removeHandler(self.screen_logger)
    if hasattr(self, 'queued_job_logger'):
        self.removeHandler(self.queued_job_logger)

    # Add separator logger
    if hasattr(self, 'separator_logger'):
        self.addHandler(self.separator_logger)

    self.info(settings.LOGGING_SEPARATOR_PLACEHOLDER)

    # Remove separator logger
    if hasattr(self, 'separator_logger'):
        self.removeHandler(self.separator_logger)

    # Restore standard loggers
    if hasattr(self, 'sys_logger'):
        self.addHandler(self.sys_logger)
    if hasattr(self, 'screen_logger'):
        self.addHandler(self.screen_logger)
    if hasattr(self, 'queued_job_logger'):
        self.addHandler(self.queued_job_logger)


class Logger(object):
    _loggers = {}

    @classmethod
    def get_logger(cls, prefix, log_level=settings.LOGGING_LEVEL,
                   to_syslog=True, to_screen=False, queued_job=None):
        if prefix in cls._loggers:
            return cls._loggers[prefix]

        syslog_path = '/var/run/syslog'\
            if platform.system() == 'Darwin' else '/dev/log'

        syslog_format = ' '.join(['DECKARD', prefix.upper(),
                                  '%(levelname)s %(pathname)s:%(lineno)s',
                                  '%(funcName)s %(message)s'])
        screen_format = ' '.join(['%(asctime)s', syslog_format])

        logger = logging.getLogger(prefix)
        logger.setLevel(log_level)

        if to_syslog:
            sys_logger = SysLogHandler(
                address=syslog_path, facility=SysLogHandler.LOG_SYSLOG)
            sys_logger_fmt = logging.Formatter(syslog_format)
            sys_logger_fmt.datefmt = '%b %d %H:%M:%S'
            sys_logger.setFormatter(sys_logger_fmt)
            logger.addHandler(sys_logger)
            logger.sys_logger = sys_logger

        if to_screen:
            screen_logger = StreamHandler()
            screen_logger_fmt = logging.Formatter(screen_format)
            screen_logger_fmt.datefmt = '%b %d %H:%M:%S'
            screen_logger.setFormatter(screen_logger_fmt)
            logger.addHandler(screen_logger)
            logger.screen_logger = screen_logger

        if queued_job:
            queued_job_logger = QueuedJobLogHandler(queued_job)
            queued_job_logger.setLevel(logging.INFO)
            queued_job_log_fmt = logging.Formatter(
                '[%(levelname)s] %(task)s %(message)s')
            queued_job_logger.setFormatter(queued_job_log_fmt)
            logger.addHandler(queued_job_logger)
            logger.queued_job_logger = queued_job_logger

            separator_logger = QueuedJobLogHandler(queued_job)
            separator_logger.setLevel(logging.DEBUG)
            separator_logger.setFormatter(logging.Formatter('%(message)s'))
            logger.separator_logger = separator_logger

        logger.separator = types.MethodType(log_separator, logger)

        cls._loggers[prefix] = logger

        return logger


class QueuedJobLogHandler(logging.Handler):
    def __init__(self, queued_job):
        logging.Handler.__init__(self)
        self._queued_job = queued_job

    def emit(self, record):
        try:
            if 'task' not in record.__dict__:
                record.__dict__.update(dict(task=u''))

            self.format(record)

            if record.exc_info:
                record.exc_text = logging._defaultFormatter.formatException(
                    record.exc_info)
            else:
                record.exc_text = ''

            msg = self.formatter.format(record).replace("  ", " ")
            self._queued_job.log.append(unicode(msg))
            db_session.commit()
        except:
            import traceback
            ei = sys.exc_info()
            traceback.print_exception(ei[0], ei[1], ei[2], None, sys.stderr)
            del ei

    def close(self):
        logging.Handler.close(self)
