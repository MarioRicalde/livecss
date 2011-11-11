# stdlib
from os.path import join, basename, dirname

# sublime
import sublime
import sublime_plugin

# local improrts
from colors import named_colors
from templates import *


#TODO:
# generate theme and syn files by lxml
# and uncolorize command
# add % rgb support

# Constants
PACKAGES_PATH = sublime.packages_path()
SUBLIME_PATH = dirname(PACKAGES_PATH)


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
            hex_color = self._rgb_to_hex(tuple(color.split(',')))
        else:
            if len(color) == 4:
                color = "#{0[1]}0{0[2]}0{0[3]}0".format(color)
            hex_color = color
        return hex_color

    @property
    def normalized(self):
        if len(self.color) == 4:
            return self.color
        return self.hex

    @property
    def undash(self):
        return self.normalized.lstrip('#')

    @property
    def opposite(self):
        rgb = self._hex_to_rgb(self.undash)
        diff = (255 - rgb[0], 255 - rgb[1], 255 - rgb[2])
        return self._rgb_to_hex(diff)

    def __repr__(self):
        return self.color

    def __eq__(self, other):
        return self.color == other.color

    def __hash__(self):
        return hash(self.color)

    def _rgb_to_hex(self, rgb):
        # rgb: tuple of r,g,b values
        return '#%02x%02x%02x' % tuple(int(x) for x in rgb)

    def _hex_to_rgb(self, hex):
        hex_len = len(hex)
        return tuple(int(hex[i:i + hex_len / 3], 16) for i in range(0, hex_len, hex_len / 3))


class State(object):
    """File state based on colors.
    Uses hash of all colors in file to save state
    """

    def __init__(self, colors):
        self._settings = sublime.load_settings('Colorized.sublime-settings')
        self.colors = colors

    def save(self):
        self._hash = str(hash(str(self.colors)))

    @property
    def is_dirty(self):
        """Indicates if new colors appeared"""
        if self._hash != str(hash(str(self.colors))):
            return True

    @property
    def _hash(self):
        return self._settings.get('hash')

    @_hash.setter
    def _hash(self, value):
        self._settings.set('hash', value)
        sublime.save_settings('Colorized.sublime-settings')


class theme(object):
    """Global object represents ST color scheme """

    _settings = sublime.load_settings('Base File.sublime-settings')

    class __metaclass__(type):
        @property
        def current_theme(cls):
            theme_path = cls._settings.get('color_scheme')
            if theme_path.startswith('Packages'):
                theme_path = join(SUBLIME_PATH, theme_path)
            return theme_path

        @current_theme.setter
        def current_theme(cls, name):
            cls._settings.set('color_scheme', name)

        @property
        def is_colorized(cls):
            if cls.name.startswith('Colorized-'):
                return True

        @property
        def path(cls):
            return dirname(cls.current_theme)

        @property
        def name(cls):
            return basename(cls.current_theme)

        @property
        def colorized_name(cls):
            """Theme name with 'Colorized-' prefix"""
            if not cls.is_colorized:
                return join(cls.path, 'Colorized-' + cls.name)
            return cls.current_theme


def add_colors(colors):
    """Returns xml ready to be inserted in color theme

    Arguments:
    colors: [Color]
    """

    colors_xml = [theme_template.format(color.undash, color.hex, color.opposite)
                  for color in colors]
    return colors_xml


def generate_color_theme(colors):
    """Generate new color theme with rules for `colors` inside.
    Then set up it as current theme.

    Arguments:
    colors: [Color]
    """

    theme_path = theme.current_theme

    with open(theme_path, 'r') as current_theme_file:
        # for now we just insert new colors after 8-th line
        # FIXME: generate xml instead
        current_theme_content = current_theme_file.readlines()
        new_colores = add_colors(set(colors))
        colorized_theme_content = current_theme_content[0:8] + new_colores + current_theme_content[8:]

    with open(theme.colorized_name, 'w') as colorized_theme_file:
        colorized_theme_file.write(''.join(colorized_theme_content))

    theme.current_theme = theme.colorized_name


def colorize_regions(view, regions, colors):
    """Colorize given `regions` through ST API.

    Arguments:
    regions: [sublime.Region], regions to colorize
    colors: [Color], colors to colorize `regions`
    """

    regions_colors = zip(regions, colors)
    for r, c  in regions_colors:
        view.add_regions(str(r), [r], c.undash)


class CssColorizeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        color_regions = self.get_color_regions()
        colors = self.get_colors(color_regions)
        state = State(colors)
        if not colors or theme.is_colorized and not state.is_dirty:
            return []
        state.save()
        generate_color_theme(colors)
        colorize_regions(self.view, color_regions, colors)

    def get_colors(self, color_regions):
        colors = [Color(self.view.substr(color)) for color in color_regions]
        return colors

    def get_color_regions(self):
        w3c = self.view.find_by_selector("support.constant.color.w3c-standard-color-name.css")
        extra_web = self.view.find_by_selector("invalid.deprecated.color.w3c-non-standard-color-name.css")
        hex_rgb = self.view.find_by_selector("constant.other.color.rgb-value.css")
        return w3c + extra_web + hex_rgb


class CssUnColorizeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.remove_regions("")


class CssColorizeEventer(sublime_plugin.EventListener):
    def on_load(self, view):
        self.view = view
        self.colorize()

    def on_modified(self, view):
        self.view = view
        self.colorize()

    def colorize(self):
        if not self.file_is_css:
            return []
        view.window().run_command("css_colorize")

    @property
    def file_is_css(self):
        any_point = self.view.sel()[0].begin()
        file_scope = self.view.scope_name(any_point).split()[0]
        if file_scope == 'source.css':
            return True
