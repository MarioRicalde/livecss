# -*- coding: utf-8 -*-

"""
    livecss.colorizer
    ~~~~~~~~~

    This module implements python helper objects.

"""

from .color import Color
from .fast_theme_generation import generate_theme_file
from .file_operatios import rm_theme
from .helpers import escape
from .state import State
from .theme import theme, uncolorized_path, colorized_path


def colorize_file(view, erase_state=False):
    """Highlights color definition regions by it's real colors.
    Erase_state setted to True forces recolorization

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

        print "Uncolorized theme path ", uncolorized_path(theme.abspath)
        colorized_theme_path = generate_theme(uncolorized_path(theme.abspath), colors)
        theme.set(colorized_theme_path)

        # remove previously used theme if any
        rm_theme(state.theme_path)
        # associate theme with file
        state.theme_path = theme.abspath


def uncolorize_file(view):
    """Removes highlighting from view,
    then delete modified theme file, set original theme
    and erase state for the view.

    """

    clear_css_regions(view)
    theme.set(uncolorized_path(theme.abspath))
    state = State(view)

    rm_theme(state.theme_path)

    state.erase()


# extract colors from file

def get_colors(view, color_regions):
    """Extracts text from `color_regions` and wraps it by :attr:`livecss.color.Color` object.

    :param color_regions: list of ST regions which contain color definition
    :return: list of colors wrapped by :attr:`livecss.color.Color` object

    """

    colors = [Color(view.substr(color)) for color in color_regions]
    return colors


def get_colored_regions(view):
    """Returns regions which contain color definition.

    :return: list of ST regions

    """

    w3c = view.find_by_selector("support.constant.color.w3c-standard-color-name.css")
    extra_web = view.find_by_selector("invalid.deprecated.color.w3c-non-standard-color-name.css")
    hex_rgb = view.find_by_selector("constant.other.color.rgb-value.css")
    rbg_percent = view.find_by_selector("constant.other.color.rgb-percentage.css")
    less_colors = view.find_by_selector("constant.other.rgb-value.css")
    return w3c + extra_web + hex_rgb + rbg_percent + less_colors


# generate new theme file

def generate_theme(theme_path, colors):
    """Generates new ST theme file with rules for new colors.

    :param theme_path: path to ST theme file
    :param colors: list of colors wrapped by :attr:`livecss.color.Color` object
    :return: newly created theme file

    """

    colorized_theme_path = colorized_path(theme.abspath)

    new_colors = (template(color) for color in set(colors))
    generate_theme_file(theme_path, new_colors, colorized_theme_path)

    return colorized_theme_path


def template(color):
    """Template to insert in theme plist file.

    :param color: :attr:`livecss.color.Color` object
    :return: plist convert ready dict

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
    """Highlights `regions` by `colors`

    :param regions: regions with color definition
    :param colors: colors to highlight these regions
    :param state: current state for this file. :attr:`livecss.state.State` object

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
    """Removes previously highlighted regions"""

    count = 0
    while count != -1:
        name = "css_color_%d" % count
        if len(view.get_regions(name)):
            view.erase_regions(name)
            count += 1
        else:
            count = -1
