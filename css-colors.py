# stdlib
from os.path import join, basename, dirname
from plistlib import readPlist as read_plist
from plistlib import writePlist as write_plist

# sublime
import sublime
import sublime_plugin

# local improrts
from colors import named_colors


#TODO:
# maybe rm out-dated theme files on fist run
# add % rgb support
# add user options

# fix:
# file opened, colorized, closed, openend -> state didn't change

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
            color = color.split(',')
            if len(color) == 4:
                hex_color = self._rgb_to_hex(tuple(color[:-1]))
            else:
                hex_color = self._rgb_to_hex(tuple(color))
        else:
            if len(color) == 4:
                color = "#{0[1]}0{0[2]}0{0[3]}0".format(color)
            hex_color = color
        return hex_color

    @property
    def undash(self):
        return self.hex.lstrip('#')

    @property
    def opposite(self):
        r, g, b = self._hex_to_rgb(self.undash)
        brightness = (r + r + b + g + g + g) / 6
        if brightness > 130:
            return '#000000'
        else:
            return '#ffffff'

    def __repr__(self):
        return self.color

    def __str__(self):
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

    def __init__(self, colors, regions, file_id):
        self._settings = sublime.load_settings('Colorized.sublime-settings')
        self.colors = colors
        self.regions = regions
        self.file_id = file_id

    def save(self):
        self._settings.set('state', {self.file_id: self.current_state})

    @property
    def is_dirty(self):
        """Indicates if new colors appeared"""

        current_state = self.current_state
        saved_state = self.saved_state
        saved_colors = [x.split(',')[0][2:-1] for x in saved_state]
        if saved_colors == self.colors:
            return
        diff = list_diff(current_state, saved_state)
        if diff:
            return True

    @property
    def saved_state(self):
        """Returns saved colors and regions if any"""

        s = self._settings.get('state')
        if not s or not s.get(self.file_id):
            return []
        return [str(x) for x in s[self.file_id]]

    @property
    def current_state(self):
        colors = [str(c) for c in self.colors]
        regions = [str(r) for r in self.regions]
        return [str(x) for x in zip(regions, colors)]

    def erase(self):
        s = self._settings.get('state')
        if s:
            self._settings.erase('state')


list_diff = lambda l1, l2: [x for x in l1 if x not in l2]
escape = lambda s: "\'" + s + "\'"


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

        @property
        def uncolorized_name(cls):
            """Remove 'Colorized-' prefix from theme's name"""

            if cls.is_colorized:
                return join(cls.path, cls.name.lstrip('Colorized-'))


def template(color):
    """Template dict to use in color theme plist generating"""

    el = {
    'name': escape(color.color),
    'scope': color.color,
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

    theme_path = theme.current_theme
    theme_plist = read_plist(theme_path)
    new_colors = (template(color) for color in set(colors))
    for el in new_colors:
        theme_plist['settings'].append(el)
    write_plist(theme_plist, theme.colorized_name)

    theme.current_theme = theme.colorized_name


def colorize_regions(view, regions, colors):
    """Colorize given `regions` through ST API.

    Arguments:
    regions: [sublime.Region], regions to colorize
    colors: [Color], colors to colorize `regions`
    """

    regions_colors = zip(regions, colors)
    for r, c  in regions_colors:
        view.add_regions(str(r), [r], c.color)


def colorize_css(view, erase_state):
    color_regions = get_color_regions(view)
    colors = get_colors(view, color_regions)
    file_id = view.file_name() or str(view.buffer_id())
    state = State(color_regions, colors, file_id)
    if erase_state:
        state.erase()
    if not colors or theme.is_colorized and not state.is_dirty:
        state.save()
        return []
    state.save()
    generate_color_theme(colors)
    colorize_regions(view, color_regions, colors)


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
    return w3c + extra_web + hex_rgb


class CssColorizeCommand(sublime_plugin.TextCommand):
    def run(self, edit, erase_state=False):
        colorize_css(self.view, erase_state)


class CssUncolorizeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        colorized_regions = get_color_regions(self.view)
        for region in colorized_regions:
            self.view.erase_regions(str(region))
        theme.current_theme = theme.uncolorized_name


class CssColorizeEventer(sublime_plugin.EventListener):
    def on_load(self, view):
        self.view = view
        if self.file_is_css:
            colorize_css(view, True)

    def on_modified(self, view):
        self.view = view
        if self.file_is_css:
            colorize_css(view, False)

    @property
    def file_is_css(self):
        any_point = self.view.sel()[0].begin()
        file_scope = self.view.scope_name(any_point).split()[0]
        if file_scope == 'source.css':
            return True
