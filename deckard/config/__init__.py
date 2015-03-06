# -*- coding: utf-8 -*-
import logging
import sys


class Settings(object):
    _settings_store = None

    def __init__(self, default_settings=None):
        self._settings_store = {}
        if default_settings:
            self.apply(default_settings)

    def __dir__(self):
        return self._settings_store.keys()

    def __iter__(self):
        for key, value in self._settings_store.items():
            yield (key, value)

    def __getattr__(self, name):
        if not name.startswith('_') and name in self._settings_store:
            return self._settings_store[name]
        else:
            return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if not name.startswith('_'):
            self._settings_store[name] = value
        else:
            object.__setattr__(self, name, value)

    def apply(self, settings_file):
        try:
            settings_module = __import__(settings_file, fromlist=['*'])
            for sm_key in [k for k in dir(settings_module)
                           if not k.startswith('__')]:
                sm_value = getattr(settings_module, sm_key)
                setattr(self, sm_key, sm_value)
            del sys.modules[settings_file]
            del settings_module
        except ImportError:
            logging.info(("Settings module \"{}\" doesn't exist. "
                          "Skipping.").format(settings_file))

settings = Settings('deckard.config.default_settings')
settings.apply('local_settings')
