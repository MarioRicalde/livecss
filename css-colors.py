# stdlib
from glob import glob
from os import remove as rm
from os.path import basename, exists
from plistlib import readPlist as read_plist
from plistlib import writePlist as write_plist

# sublime
import sublime_plugin

# local imports
from theme import *
from state import State
from settings import Settings
from color import Color


user_settings = Settings('CSS-colors.sublime-settings')


def clear_css_regions(view):
    count = 0
    while count != -1:
        name = "css_color_%d" % count
        if len(view.get_regions(name)) != 0:
            view.erase_regions(name)
            count += 1
        else:
            count = -1


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

escape = lambda s: "\'" + s + "\'"


def generate_color_theme(colors):
    """Generate new color theme with rules for `colors` inside.
    Then set up it as current theme.

    Arguments:
    colors: [Color]
    """

    theme_path = theme.abspash
    theme_plist = read_plist(theme_path)
    colorized_theme_path = colorized_path(theme)

    new_colors = (template(color) for color in set(colors))
    for el in new_colors:
        theme_plist['settings'].append(el)
    write_plist(theme_plist, colorized_theme_path)

    if is_colorized(theme):
        # check may be wrong
        theme.set(colorized_theme_path)
        rm(theme_path)
        # check if exists
        rm(theme_path + '.cache')


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
        print "Generating theme"
        generate_color_theme(colors)
    state.save()


def get_colors(view, color_regions):
    """Turns regions into [Color]"""
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


def colorize_if_not(view):
    if not is_colorized(theme):
        colorize_css(view, True)


def clean_themes_folder():
    theme_folder = theme.dirname
    current_theme = theme.name
    themes = glob(theme_folder + '/*')
    colored_themes = [t for t in themes if basename(t).startswith('Colorized-')]
    themes_except_current = [t for t in colored_themes if basename(t) != current_theme]
    for color_theme in themes_except_current:
        if exists(color_theme):
            rm(color_theme)


class CssColorizeCommand(sublime_plugin.TextCommand):
    def run(self, edit, erase_state=False):
        colorize_css(self.view, erase_state)


class CssUncolorizeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        clear_css_regions(self.view)
        if is_colorized(theme):
            theme.set(uncolorized_path(uncolorized_path))
            clean_themes_folder()


class CssColorizeEventer(sublime_plugin.EventListener):
    def __init__(self):
        # on plugin load
        clean_themes_folder()

    def on_load(self, view):
        if not user_settings.dynamic_highlight:
            return
        self.view = view
        theme.on_select_new_theme(lambda: colorize_if_not(view))
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
