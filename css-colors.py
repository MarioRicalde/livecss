# stdlib
from os import remove as rm
from os.path import join, basename, dirname, normpath, relpath
from plistlib import readPlist as read_plist
from plistlib import writePlist as write_plist
from random import randint
import re

# sublime
import sublime
import sublime_plugin

# local improrts
from colors import named_colors

# fix bug whet typing rgb color
# add_regions only for changed regions

# Constants
PACKAGES_PATH = sublime.packages_path()
SUBLIME_PATH = dirname(PACKAGES_PATH)


def clear_css_regions(view):
    count = 0
    while count != -1:
        name = "css_color_%d" % count
        if len(view.get_regions(name)) != 0:
            view.erase_regions(name)
            count += 1
        else:
            count = -1


class user_settings(object):
    """Global object represents user settings
    """

    _settings_file = 'CSS-colors.sublime-settings'
    _settings = sublime.load_settings(_settings_file)

    class __metaclass__(type):
        def __new__(typ, *args, **kwargs):
            """Set inisial settings"""

            obj = type.__new__(typ, *args, **kwargs)
            obj._init_if_not_exists()
            return obj

        @property
        def dynamic_highlight(cls):
            # cls._init_if_not_exists()
            s = cls._settings.get('dynamic_highlight')
            return s

        @dynamic_highlight.setter
        def dynamic_highlight(cls, value):
            cls._settings.set('dynamic_highlight', value)
            cls.save()

        def save(cls):
            sublime.save_settings(cls._settings_file)

        def _init_if_not_exists(cls):
            if cls.dynamic_highlight == None:
                cls._settings.set('dynamic_highlight', True)
                cls.save()


class Color(object):
    """Convenience to work with colors"""

    def __init__(self, color):
        self.color = color

    @property
    def hex(self):
        color = self.color
        if color in named_colors:
            hex_color = named_colors[color]
        elif not color.startswith('#'):
            # if rgb
            color = color.split(',')
            hex_color = self._rgb_to_hex(tuple(color))
        else:
            if len(color) == 4:  # FIXME
                # 3 sign hex
                color = "#{0[1]}{0[1]}{0[2]}{0[2]}{0[3]}{0[3]}".format(color)
            hex_color = color

        return hex_color

    @property
    def undash(self):
        return self.hex.lstrip('#')

    @property
    def opposite(self):
        r, g, b = self._hex_to_rgb(self.undash)
        brightness = (r + r + b + b + g + g) / 6
        if brightness > 130:
            return '#000000'
        else:
            return '#ffffff'

    def __repr__(self):
        return self.hex

    def __str__(self):
        return self.hex

    def __eq__(self, other):
        return self.hex == other

    def __hash__(self):
        return hash(self.hex)

    def _rgb_to_hex(self, rgb):
        if str(rgb[0])[-1] == '%':
            # percentage notation
            r = int(rgb[0].rstrip('%')) * 255 / 100
            g = int(rgb[1].rstrip('%')) * 255 / 100
            b = int(rgb[2].rstrip('%')) * 255 / 100
            return self._rgb_to_hex((r, g, b))

        if len(rgb) == 4:
            #rgba
            rgb = rgb[0:3]

        return '#%02x%02x%02x' % tuple(int(x) for x in rgb)

    def _hex_to_rgb(self, hex):
        hex_len = len(hex)
        return tuple(int(hex[i:i + hex_len / 3], 16) for i in range(0, hex_len, hex_len / 3))


class State(object):
    """File state based on colors.
    Uses hash of all colors in file to save state
    """

    def __init__(self, colors, file_id):
        self._settings = sublime.load_settings('Colorized.sublime-settings')
        self.colors = colors
        self.file_id = file_id

    def save(self):
        state = {self.file_id: {'colors': [str(x) for x in self.colors]}}
        self._settings.set('state', state)

    @property
    def need_generate_new_color_file(self):
        saved_colors = self.saved_state['colors']
        if set(self.colors) - set(saved_colors):
            return True

    @property
    def saved_state(self):
        """Returns saved colors if any
        or empty state
        """

        s = self._settings.get('state')
        if not s or not s.get(self.file_id):
            return {'colors': []}
        return s[self.file_id]

    def erase(self):
        s = self._settings.get('state')
        if s:
            self._settings.erase('state')


list_diff = lambda l1, l2: [x for x in l1 if x not in l2]
escape = lambda s: "\'" + s + "\'"


#TODO: add fallbacks on errors
class theme(object):
    """Global object represents ST color scheme """

    _settings = sublime.load_settings('Base File.sublime-settings')
    _prefix = 'Colorized-'

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

        @property
        def is_colorized(cls):
            if cls.name.startswith(cls._prefix):
                return True

        def set(cls, theme):
            """theme: abs or relpath to PACKAGES_PATH"""
            cls._settings.set('color_scheme', theme)

        @property
        def colorized_path(cls):
            return join(cls.dirname, cls.colorized_name)

        @property
        def uncolorized_path(cls):
            return join(cls.dirname, cls.uncolorized_name)

        @property
        def uncolorized_name(cls):
            if cls.is_colorized:
                s = re.search(cls._prefix + "(\d+-)?(?P<Name>.*)", cls.name)
                theme_name = s.group('Name')
                return theme_name
            return cls.name

        @property
        def colorized_name(cls):
            r = str(randint(1, 10 ** 15)) + '-'
            return cls._prefix + r + cls.uncolorized_name


def template(color):
    """Template dict to use in color theme plist generating"""

    el = {
        'name': escape(color.hex),
        'scope': color.hex,
        'settings': {
            'background': color.hex,
            'foreground': color.opposite
        }
    }
    return el


def generate_color_theme(colors):
    """Generate new color theme with rules for `colors` inside.
    Then set up it as current theme.

    Arguments:
    colors: [Color]
    """

    theme_path = theme.abspash
    theme_plist = read_plist(theme_path)
    colorized_theme_path = theme.colorized_path

    new_colors = (template(color) for color in set(colors))
    for el in new_colors:
        theme_plist['settings'].append(el)
    write_plist(theme_plist, colorized_theme_path)

    if theme.is_colorized:
        rm(theme.abspash)
        rm(theme.abspash + '.cache')

    theme.set(colorized_theme_path)


def colorize_regions(view, regions, colors):
    """Colorize given `regions` through ST API.

    Arguments:
    regions: [sublime.Region], regions to colorize
    colors: [Color], colors to colorize `regions`
    """

    regions_colors = zip(regions, colors)
    # Clear all available colored regions
    clear_css_regions(view)
    # Color regions
    count = 0
    for r, c  in regions_colors:
        name = "css_color_%d" % count
        view.add_regions(name, [r], c.hex)
        count += 1


def colorize_css(view, erase_state):
    color_regions = get_color_regions(view)
    colors = get_colors(view, color_regions)
    file_id = view.file_name() or str(view.buffer_id())
    state = State(colors, file_id)
    if erase_state:
        state.erase()
    if not colors:
        return
    colorize_regions(view, color_regions, colors)
    if state.need_generate_new_color_file:
        generate_color_theme(colors)
    state.save()


def get_colors(view, color_regions):
    """Turnes regions into [Color]"""
    colors = [Color(view.substr(color)) for color in color_regions]
    return colors


def get_color_regions(view):
    """Search for color properties in current css file.
    Returns sublime.Region"""

    w3c = view.find_by_selector("support.constant.color.w3c-standard-color-name.css")
    extra_web = view.find_by_selector("invalid.deprecated.color.w3c-non-standard-color-name.css")
    hex_rgb = view.find_by_selector("constant.other.color.rgb-value.css")
    rbg_percent = view.find_by_selector("constant.other.color.rgb-percentage.css")
    return w3c + extra_web + hex_rgb + rbg_percent


def erase_colorized_regions(view, regions):
    for region in regions:
        view.erase_regions(str(region))


class CssColorizeCommand(sublime_plugin.TextCommand):
    def run(self, edit, erase_state=False):
        colorize_css(self.view, erase_state)


class CssUncolorizeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        clear_css_regions(self.view)
        if theme.is_colorized:
            rm(theme.abspash)
            rm(theme.abspash + '.cache')
            theme.set(theme.uncolorized_path)


# TODO: activate on change
class CssColorizeEventer(sublime_plugin.EventListener):
    def on_load(self, view):
        if not user_settings.dynamic_highlight:
            return
        self.view = view
        if self.file_is_css:
            colorize_css(view, True)

    def on_modified(self, view):
        if not user_settings.dynamic_highlight:
            return
        self.view = view
        if self.file_is_css:
            colorize_css(view, False)

    @property
    def file_is_css(self):
        any_point = self.view.sel()[0].begin()
        file_scope = self.view.scope_name(any_point).split()[0]
        if file_scope == 'source.css':
            return True


class ToggleAutoCssColorize(sublime_plugin.WindowCommand):
    def run(self):
        if user_settings.dynamic_highlight:
            user_settings.dynamic_highlight = False
            self.window.run_command('css_uncolorize')
        else:
            user_settings.dynamic_highlight = True
            self.window.run_command('css_colorize', {'erase_state': True})
