# -*- coding: utf-8 -*-

"""
    livecss.config
    ~~~~~~~~~

    Wrapper around ST settings.

"""

from .wrappers import PerFileConfig


class Config(PerFileConfig):
    """Object which wraps ST settings entity.
    Properties started with `global_` are global setting.
    Properties started with `local_` are unique for file.
    Default value is True.

    """

    def __init__(self, view):
        super(Config, self).__init__(view.buffer_id(), 'Livecss.sublime-settings', in_memory=False)

    def __getattribute__(self, attr):
        if attr.startswith("global_"):
            rval = self._s[attr]
        else:
            rval = super(Config, self).__getattribute__(attr)
        # default value if True
        return True if rval == None else rval

    def __setattr__(self, attr, value):
        if attr.startswith("global_"):
            self._s[attr] = value
        else:
            return super(Config, self).__setattr__(attr, value)
