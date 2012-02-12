"""
    livecss.colorizer
    ~~~~~~~~~

    This module implements python helper objects.

    :copyright: (c) 2012 by Alexandr Skurihin.
    :license: BSD, see LICENSE for more details.

"""

from color import Color
from fast_theme_generation import generate_theme_file
from file_operatios import rm_theme
from helpers import escape
from state import State
from theme import theme, uncolorized_path, colorized_path

__all__ = ['colorize_file', 'uncolorize_file']


def colorize_file(view, erase_state=False):
    """Highlight color definition regions
    by it's real colors
    """

    colored_regions = get_colored_regions(view)
    colors = get_colors(view, colored_regions)
    if not colors:
        return

    state = State(view, colors, colored_regions)
    if erase_state:
        state.erase()

    if not state.is_dirty:
        return

    highlight_regions(view, colored_regions, colors, state)

    if state.need_generate_theme_file:

        colorized_theme = generate_theme(uncolorized_path(theme.abspath), colors)
        theme.set(colorized_theme)

        # remove previously used theme if any
        rm_theme(state.theme_path)
        # associate theme with file
        state.theme_path = theme.abspath


def uncolorize_file(view):
    """
    Remove highlighting from view,
    then delete modified theme file, set original theme
    and erase state for the view.

    :param  :attr:`sublime.view` view
    """

    clear_css_regions(view)
    theme.set(uncolorized_path(theme.abspath))
    state = State(view)

    rm_theme(state.theme_path)

    state.erase()


# extract colors from file

def get_colors(view, color_regions):
    """
    Extract text from @color_regions and wrap it by Color object.

    @param {sublime.view} view
    @param {[sublime.Region]} color_regions
    @return {[Color]}

    """
    colors = [Color(view.substr(color)) for color in color_regions]
    return colors


def get_colored_regions(view):
    """
    Looks for color definitions.

    @param {sublime.view}
    @return {[sublime.Region]}

    """

    w3c = view.find_by_selector("support.constant.color.w3c-standard-color-name.css")
    extra_web = view.find_by_selector("invalid.deprecated.color.w3c-non-standard-color-name.css")
    hex_rgb = view.find_by_selector("constant.other.color.rgb-value.css")
    rbg_percent = view.find_by_selector("constant.other.color.rgb-percentage.css")
    less_colors = view.find_by_selector("constant.other.rgb-value.css")
    return w3c + extra_web + hex_rgb + rbg_percent + less_colors


# generate new theme file

def generate_theme(theme_path, colors):
    """
    Generate new ST theme file
    with highlighting rules definitions for new colors.

    @param {str}   theme_path
    @param {[Color]} colors
    @return {str}

    """

    colorized_theme_path = colorized_path(theme.abspath)

    new_colors = (template(color) for color in set(colors))
    generate_theme_file(theme_path, new_colors, colorized_theme_path)

    return colorized_theme_path


def template(color):
    """
    Template to insert in theme plist file.

    @param {Color} color
    @return {dict}

    """

    return {
        'name': escape(color.hex),
        'scope': color.hex,
        'settings': {
            'background': color.hex,
            'foreground': color.opposite
        }
    }


# add/remove regions from view

def highlight_regions(view, regions, colors, state):
    """
    Highlight @regions by @colors

    @param {[sublime.Region]}
    @param {[Color]}

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
    state.count = count


def clear_css_regions(view):
    """
    Remove previously highlighted regions.

    @param {sublime.view} view

    """

    count = 0
    while count != -1:
        name = "css_color_%d" % count
        if len(view.get_regions(name)):
            view.erase_regions(name)
            count += 1
        else:
            count = -1
