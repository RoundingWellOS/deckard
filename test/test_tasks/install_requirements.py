# -*- coding: utf-8 -*-
from ..task import TaskBase


class InstallRequirements(TaskBase):
    """
    Install requirements
    """

    def process(self, context):
        context['install_requirements_addition'] = "Meh!"
        self._logger.info("Installing requirements with context %s", context)
