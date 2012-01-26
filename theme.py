from os.path import join, basename, dirname, normpath, relpath
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
        def abspash(cls):
            theme_path = cls._settings.get('color_scheme') or ""

            if theme_path.startswith('Packages'):
                theme_path = join(SUBLIME_PATH, theme_path)

            return normpath(theme_path)

        @property
        def relpath(cls):
            return relpath(cls.abspash, SUBLIME_PATH)

        @property
        def dirname(cls):
            return dirname(cls.abspash)

        @property
        def name(cls):
            return basename(cls.abspash)

        def set(cls, theme):
            """theme: abs or relpath to PACKAGES_PATH"""
            cls._settings.set('color_scheme', theme)

        def on_select_new_theme(cls, callback):
            cls._settings.add_on_change('color_scheme', callback)


def is_colorized(theme):
    if theme.name.startswith(theme.prefix):
        return True


def colorized_path(theme):
    return join(theme.dirname, colorized_name(theme))


def colorized_name(theme):
    random = str(randint(1, 10 ** 15)) + '-'
    return theme.prefix + random + uncolorized_name(theme)


def uncolorized_name(theme):
    if is_colorized(theme):
        s = re.search(theme.prefix + "(\d+-)?(?P<Name>.*)", theme.name)
        theme_name = s.group('Name')
        return theme_name
    return theme.name


def uncolorized_path(theme):
    return join(theme.dirname, uncolorized_name(theme))