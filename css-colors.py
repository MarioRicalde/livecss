# stdlib
from os import mkdir
from os.path import join, exists, basename
from shutil import rmtree as rm

# sublime
import sublime
import sublime_plugin

# local improrts
from colors import named_colors
from templates import *


#TODO:
# generate theme and syn files by lxml

# Constants

PACKAGES_PATH = sublime.packages_path()
USER_DIR_PATH = join(PACKAGES_PATH, 'User/')
COLORIZED_PATH = join(USER_DIR_PATH, 'Colorized/')


class CssColorsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.apply_original_syntax()
        colors = self.colors_in_current_file()
        if theme_is_colorized() and not colors_changed(colors):
            self.apply_colorized_syntax()
            return
        self.prepare_env()
        save_colors_hash(colors)
        generate_syntax(self.view, colors)
        highlight(colors)

    def colors_in_current_file(self):
        color_regions = self.find_colors()
        colors = set(Color(self.view.substr(color)) for color in color_regions)
        # normalized_to_hex_colors = set(to_hex(hex_rgb_colors))
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

    def find_colors(self):
        w3c = self.view.find_by_selector("support.constant.color.w3c-standard-color-name.css")
        extra_web = self.view.find_by_selector("invalid.deprecated.color.w3c-non-standard-color-name.css")
        hex_rgb = self.view.find_by_selector("constant.other.color.rgb-value.css")
        return w3c + extra_web + hex_rgb


class Color(object):
    def __init__(self, color):
        self.color = color

    @property
    def hex(self):
        return to_hex(self.color)

    @property
    def syntax_template(self):
        return template_for(self.color)

    @property
    def undash(self):
        return self.hex[1:]

    @property
    def opposite(self):
        return opposite(self.hex)

    def __repr__(self):
        return self.color

    def __eq__(self, other):
        return self.color == other.color

    def __hash__(self):
        return hash(self.color)


def save_colors_hash(colors):
    settings = "Colorized.sublime-settings"
    s = sublime.load_settings(settings)
    s.set('hash', str(hash(str(colors))))
    sublime.save_settings(settings)


def colors_changed(colors):
    s = sublime.load_settings("Colorized.sublime-settings")
    h = s.get('hash')
    if h != str(hash(str(colors))):
        return True


def theme_is_colorized():
    if basename(get_current_theme()).startswith('Colorized-'):
        return True


def to_hex(color):
    if color in named_colors:
        hex_color = named_colors[color]

    elif not color.startswith('#'):

        hex_color = rgb_to_hex(tuple(color.split(',')))
    else:
        hex_color = color
    return hex_color


def template_for(color):
    if color in named_colors:
        t = "(%s)\\b" % color
    elif not color.startswith('#'):
        t = "(rgb)(\(%s\))(?x)" % color
    else:
        t = "(#)(%s)\\b" % color[1:]
    return t


def rgb_to_hex(rgb):
    # rgb: tuple of r,g,b values
    return '#%02x%02x%02x' % tuple(int(x) for x in rgb)


def opposite(hex_color):
    opp_int = 16777215 - int(hex_color[1:], 16)
    opp_hex = hex(opp_int)
    return "#" + opp_hex[0] + opp_hex[2:]


def add_scopes(colors):
    """
    Add given scopes to syntax file, sufixed by 'css-colorize.css'
    """

    scopes_xml = [syntax_color_template.format(color.syntax_template, color.undash)
                                                                for color in colors]
    return template.format('\n'.join(scopes_xml)).split()


def generate_syntax(view, color_codes):

    with open(join(PACKAGES_PATH, 'CSS/CSS.tmLanguage')) as syn_file:
        syn_file_content = syn_file.readlines()
        new_rules = add_scopes(color_codes)
        colorized = syn_file_content[0:553] + include.split() + syn_file_content[553:]
        colorized = colorized[0:537] + new_rules + colorized[537:]

    # write new color rules to newly crated syntax file
    with open(COLORIZED_PATH + "Colorized-CSS.tmLanguage", 'w') as syntax_f:
        syntax_f.write(''.join(colorized))

    view.set_syntax_file(COLORIZED_PATH + "Colorized-CSS.tmLanguage")


def get_current_theme():
    s = sublime.load_settings("Base File.sublime-settings")
    theme_path = s.get('color_scheme').split('/')
    if theme_path[0]:
        theme = join(PACKAGES_PATH, *theme_path[1:])
    else:
        theme = join(COLORIZED_PATH, theme_path[-1])
    return theme


def set_current_theme(name):
    s = sublime.load_settings("Base File.sublime-settings")
    return s.set('color_scheme', name)


def add_colors(colors):
    """
    Add given scopes to syntax file, sufixed by 'css-colorize.css'
    """
    colors_xml = [theme_templ.format(color.undash, color.hex, color.opposite) for color in colors]
    return colors_xml


def highlight(colors):
    """highlight [scopes] with [colors]
    `colors` - list of color names (if hex -> without #)
    """
    theme_path = get_current_theme()
    theme = basename(theme_path)
    with open(theme_path) as fp:
        theme_content = fp.readlines()
        new_colores = add_colors(colors)
        colorized_theme = theme_content[0:8] + new_colores + theme_content[8:]

    with open(join(COLORIZED_PATH, 'Colorized-' + theme), 'w') as f:
        f.write(''.join(colorized_theme))

    set_current_theme(join(COLORIZED_PATH, 'Colorized-' + theme))
