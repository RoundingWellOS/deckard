# -*- coding: utf-8 -*-
from ..task import TaskBase


class CreateVirtualenv(TaskBase):
    """
    Creates a virtualenv
    """

    def process(self, context):
        context['virtualenv_addition'] = "hello!"
        self._logger.info("Creating a virtualenv with context %s", context)
