from os.path import join, basename, dirname, normpath, relpath, exists
from random import randint
import re

import sublime

PACKAGES_PATH = sublime.packages_path()
SUBLIME_PATH = dirname(PACKAGES_PATH)


#TODO: add fallbacks on errors
class theme(object):
    """Global object represents ST color scheme """

    _settings = sublime.load_settings('Base File.sublime-settings')
    prefix = 'Colorized-'

    class __metaclass__(type):
        @property
        def abspath(cls):
            theme_path = cls._settings.get('color_scheme') or ""

            if theme_path.startswith('Packages'):
                theme_path = join(SUBLIME_PATH, theme_path)

            return normpath(theme_path)

        @property
        def relpath(cls):
            return relpath(cls.abspath, SUBLIME_PATH)

        @property
        def dirname(cls):
            return dirname(cls.abspath)

        @property
        def name(cls):
            return basename(cls.abspath)

        def set(cls, theme_path):
            """theme: abs or relpath to PACKAGES_PATH"""
            if exists(theme_path):
                cls._settings.set('color_scheme', theme_path)

        def on_select_new_theme(cls, callback):
            cls._settings.add_on_change('color_scheme', callback)

        @property
        def is_colorized(self):
            if self.name.startswith(self.prefix):
                return True

        @property
        def colorized_path(self):
            return join(self.dirname, self.colorized_name)

        @property
        def colorized_name(self):
            random = str(randint(1, 10 ** 15)) + '-'
            return self.prefix + random + self.uncolorized_name

        @property
        def uncolorized_name(self):
            if self.is_colorized:
                s = re.search(self.prefix + "(\d+-)?(?P<Name>.*)", self.name)
                self_name = s.group('Name')
                return self_name
            return self.name

        @property
        def uncolorized_path(self):
            return join(self.dirname, self.uncolorized_name)
