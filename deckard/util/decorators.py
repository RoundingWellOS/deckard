# -*- coding: utf-8 -*-
from functools import wraps
import logging
import os
import tempfile
import sys


def pidfile(func):
    @wraps(func)
    def _decorator(*args, **kwargs):
        pidfile_name = 'deckard_{}.pid'.format(func.func_name)
        pidfile_path = os.path.join(tempfile.gettempdir(), pidfile_name)
        if os.path.isfile(pidfile_path):
            with open(pidfile_path, 'r') as f:
                pid = int(f.read())
            try:
                os.kill(pid, 0)
                logging.error(("Process already running. PID: {}. "
                               "Exiting.").format(pid))
            except OSError:
                logging.error(("Pidfile exists, but process not running. "
                               "Removing pidfile, then exiting. Please "
                               "restart the script or whatever."))
                os.unlink(pidfile_path)
            sys.exit(1)
        else:
            with open(pidfile_path, 'w') as f:
                f.write(str(os.getpid()))

        def remove_pid(*args, **kwargs):
            try:
                func(*args, **kwargs)
            finally:
                os.unlink(pidfile_path)

        return remove_pid(*args, **kwargs)
    return _decorator
