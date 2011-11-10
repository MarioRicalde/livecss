# stdlib
from os import mkdir
from os.path import join, exists, basename, dirname
from shutil import rmtree as rm
import time

# sublime
import sublime
import sublime_plugin

# local improrts
from colors import named_colors
from templates import *


#TODO:
# generate theme and syn files by lxml
# improove generating opposite color (? use only white or black for fg)
# add % rgb support

# Constants
PACKAGES_PATH = sublime.packages_path()
USER_DIR_PATH = join(PACKAGES_PATH, 'User/')
COLORIZED_PATH = join(USER_DIR_PATH, 'Colorized/')


class CssColorsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        t_start = time.time()
        self.apply_original_syntax()
        colors = self.colors_in_current_file()
        state = State(colors)
        print "theme.is_colorized", theme.is_colorized
        if theme.is_colorized and not state.dirty:
            self.apply_colorized_syntax()
            t_end = time.time()
            print t_end - t_start
            return
        self.prepare_env()
        state.save()
        highlight(colors)
        self.apply_colorized_syntax()
        t_end = time.time()
        print t_end - t_start

    def colors_in_current_file(self):
        color_regions = self._find_colors()
        colors = set(Color(self.view.substr(color)) for color in color_regions)
        return colors

    def prepare_env(self):
        if not exists(COLORIZED_PATH):
            mkdir(COLORIZED_PATH)
        else:
            rm(COLORIZED_PATH)
            mkdir(COLORIZED_PATH)

    def apply_colorized_syntax(self):
        self.view.set_syntax_file(COLORIZED_PATH + "Colorized-CSS.tmLanguage")

    def apply_original_syntax(self):
        self.view.set_syntax_file("Packages/CSS/CSS.tmLanguage")

    def _find_colors(self):
        w3c = self.view.find_by_selector("support.constant.color.w3c-standard-color-name.css")
        extra_web = self.view.find_by_selector("invalid.deprecated.color.w3c-non-standard-color-name.css")
        hex_rgb = self.view.find_by_selector("constant.other.color.rgb-value.css")
        return w3c + extra_web + hex_rgb


class Color(object):
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
            hex_color = color
        return hex_color

    @property
    def syntax_template(self):
        color = self.color
        if color in named_colors:
            t = '(%s)\\b' % color
        elif not color.startswith('#'):
            t = "(rgb)(\(%s\))(?x)" % color
        else:
            t = '(#)(%s)\\b' % self.undash
        return t

    @property
    def undash(self):
        return self.hex[1:]

    @property
    def opposite(self):
        opp_int = 16777215 - int(self.undash, 16)
        opp_hex = hex(opp_int)
        return "#" + opp_hex[0] + opp_hex[2:]

    def __repr__(self):
        return self.color

    def __eq__(self, other):
        return self.color == other.color

    def __hash__(self):
        return hash(self.color)

    def _rgb_to_hex(self, rgb):
        # rgb: tuple of r,g,b values
        return '#%02x%02x%02x' % tuple(int(x) for x in rgb)


class State:
    def __init__(self, colors):
        self.colors = colors

    def save(self):
        settings = 'Colorized.sublime-settings'
        s = sublime.load_settings(settings)
        s.set('hash', str(hash(str(self.colors))))
        sublime.save_settings(settings)

    @property
    def dirty(self):
        s = sublime.load_settings('Colorized.sublime-settings')
        h = s.get('hash')
        if h != str(hash(str(self.colors))):
            return True


class theme(object):
    """Global object
    represents sublimetext color scheme
    """

    class __metaclass__(type):
        @property
        def current_theme(cls):
            s = sublime.load_settings('Base File.sublime-settings')
            theme_path = s.get('color_scheme').split('/')
            if theme_path[0]:
                theme = join(PACKAGES_PATH, *theme_path[1:])
            else:
                theme = join(COLORIZED_PATH, theme_path[-1])
            return theme

        @current_theme.setter
        def current_theme(cls, name):
            s = sublime.load_settings("Base File.sublime-settings")
            s.set('color_scheme', name)

        @property
        def is_colorized(cls):
            if cls.name.startswith('Colorized-'):
                return True

        @property
        def path(cls):
            return dirname(cls.current_theme)

        @property
        def un_colorized_name(cls):
            if cls.is_colorized:
                return cls.current_theme
            return cls.path + cls.name[10:]

        @property
        def colorized_name(cls):
            if not cls.is_colorized:
                return cls.path + '/Colorized-' + cls.name

        @property
        def name(cls):
            return basename(cls.current_theme)


def add_scopes(colors):
    """
    Add given scopes to syntax file, sufixed by 'css-colorize.css'
    """

    scopes_xml = [syntax_color_template.format(color.syntax_template,
                  color.undash) for color in colors]
    return template.format('\n'.join(scopes_xml)).split()


def generate_syntax(colors):
    with open(PACKAGES_PATH + '/CSS/CSS.tmLanguage') as syn_file:
        syn_file_content = syn_file.readlines()
        new_rules = add_scopes(colors)
        colorized = syn_file_content[0:553] + include.split() + syn_file_content[553:]
        colorized = colorized[0:537] + new_rules + colorized[537:]

    with open(COLORIZED_PATH + "Colorized-CSS.tmLanguage", 'w') as syntax_f:
        syntax_f.write(''.join(colorized))


def add_colors(colors):
    """Add given scopes to syntax file, sufixed by 'css-colorize.css'"""

    colors_xml = [theme_templ.format(color.undash, color.hex, color.opposite)
                  for color in colors]
    return colors_xml


def generate_color_theme(colors):
    """highlight [scopes] with [colors]
    `colors` - list of color names (if hex -> without #)
    """

    theme_path = theme.current_theme
    with open(theme_path) as fp:
        theme_content = fp.readlines()
        new_colores = add_colors(colors)
        colorized_theme = theme_content[0:8] + new_colores + theme_content[8:]

    with open(theme.colorized_name, 'w') as f:
        f.write(''.join(colorized_theme))

    theme.current_theme = theme.colorized_name


def highlight(colors):
    generate_syntax(colors)
    generate_color_theme(colors)
