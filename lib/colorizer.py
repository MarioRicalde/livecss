# stdlib

from plistlib import readPlist as read_plist
from plistlib import writePlist as write_plist


# local imports
from theme import *
from state import State
from config import Config
from color import Color
from utils import *
from debug import *

__all__ = ['colorize_file', 'uncolorize_file']


def colorize_file(view, erase_state=False):
    """Highlight color definition regions
    by it's real colors

    @param [sublime.view] view
    @param [bool] erase_state: use saved state for this file

    """
    #TODO: add erase_state handling

    colored_regions = get_colored_regions(view)
    colors = get_colors(view, colored_regions)
    if not colors:
        return

    current_file = file_id(view)
    state = State(current_file, colors)

    highlight_regions(view, colored_regions, colors)

    if state.need_generate_theme_file:

        theme_path = state.theme_path or theme.abspath
        colorized_theme = generate_theme(theme_path, colors)
        theme.set(colorized_theme)

        if state.theme_path:
            rm_if_exists(state.theme_path)
            rm_if_exists(state.theme_path + '.cache')

        state.theme_path = theme.abspath


def uncolorize_file(view):
    """Remove highlighting from view,
    then delete modified theme file, set original theme
    and erase state for the view.

    @param [sublime.view] view

    """

    clear_css_regions(view)
    theme.set(theme.uncolorized_path)
    state = State(file_id(view))

    rm_if_exists(state.theme_path)
    rm_if_exists(state.theme_path + '.cache')

    state.erase()


# extract colors from file


def get_colors(view, color_regions):
    """Extract text from @color_regions and wrap it by Color object.

    @param [sublime.view] view
    @param [sublime.Region] color_regions
    @return [Color]

    """
    colors = [Color(view.substr(color)) for color in color_regions]
    return colors


def get_colored_regions(view):
    """Looks for color definitions.

    @param [sublime.view]
    @return [sublime.Region]

    """

    w3c = view.find_by_selector("support.constant.color.w3c-standard-color-name.css")
    extra_web = view.find_by_selector("invalid.deprecated.color.w3c-non-standard-color-name.css")
    hex_rgb = view.find_by_selector("constant.other.color.rgb-value.css")
    rbg_percent = view.find_by_selector("constant.other.color.rgb-percentage.css")
    return w3c + extra_web + hex_rgb + rbg_percent


# generate new theme file


def generate_theme(theme_path, colors):
    """Generate new ST theme file
    with highlighting rules definitions for new colors.

    @param [str]   theme_path
    @param [Color] colors

    """

    theme_plist = read_plist(theme_path)
    colorized_theme_path = theme.colorized_path

    new_colors = (template(color) for color in set(colors))
    for el in new_colors:
        theme_plist['settings'].append(el)
    write_plist(theme_plist, colorized_theme_path)

    return colorized_theme_path


def template(color):
    """Template to insert in theme plist file.

    @param [Color] color
    @return [dict]

    """

    return {
        'name': escape(color.hex),
        'scope': color.hex,
        'settings': {
            'background': color.hex,
            'foreground': color.opposite
        }
    }


def highlight_regions(view, regions, colors):
    # TODO: colorize based on file_id
    #       - they defined only for given view
    """Highlight @regions by @colors

    @param [sublime.Region]
    @param [Color]

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


def clear_css_regions(view):
    """Remove previously highlighted regions.

    @param [sublime.view] view

    """

    count = 0
    while count != -1:
        name = "css_color_%d" % count
        if len(view.get_regions(name)) != 0:
            view.erase_regions(name)
            count += 1
        else:
            count = -1

# add later

# add to file change event (on_activate)
# theme.set(state.theme_path) # why ?
