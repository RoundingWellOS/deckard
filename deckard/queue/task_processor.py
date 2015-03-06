# -*- coding: utf-8 -*-
from .task import TaskBase


class TaskProcessor(object):
    """
    Handles loading and proxying process requests to individual tasks.
    """

    def __init__(self, task, working_directory, stages, logger):
        self._working_directory = working_directory
        self._stages = stages
        self._logger = logger

        self._task = self._load_task(task)

    def _log(self, *args):
        self._logger.info(*args, extra=dict(task=self.name))

    def _load_task(self, task):
        parts = task['module'].split('.')
        module_path = '.'.join(parts[:-1])
        klass = parts[-1:][0]

        module = __import__(module_path, fromlist=['*'])
        task = getattr(module, klass)(self._working_directory,
                                      self._stages, self._logger)

        if not isinstance(task, TaskBase):
            raise TypeError("Tasks must inherit from TaskBase")

        return task

    @property
    def name(self):
        return self._task.name

    @property
    def description(self):
        return self._task.__doc__.strip()

    def process(self, context):
        self._log("START")
        self._task.process(context)
        self._log("END")
