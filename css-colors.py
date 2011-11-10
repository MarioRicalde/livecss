from os.path import join, exists, basename
from os import mkdir
import sublime
import sublime_plugin
from shutil import rmtree as rm


#alg:
# select all colors:
# rgb and named colors to hex form
# read CSS.tmLanguage file to memory
#   mix with generated scope names for each color
#   write it by different name
#   before exit rm new file#
# use add_regions to colorize regions
# reapply sytntax and theme files

# Constants

PACKAGES_PATH = sublime.packages_path()
USER_DIR_PATH = join(PACKAGES_PATH, 'User')
COLORIZED_PATH = join(USER_DIR_PATH, 'Colorized')


class CssColorsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.init()
        colors = self.colors_in_current_file()
        generate_syntax(self.view, colors)
        highlight(colors)

    def colors_in_current_file(self):
        colors_by_name = self.view.find_by_selector("support.constant.color.w3c-standard-color-name.css")
        hex_rgb_regions = self.view.find_by_selector("constant.other.color.rgb-value.css")
        hex_rgb_colors = [self.view.substr(color) for color in hex_rgb_regions + colors_by_name]
        normalized_to_hex_colors = set(normalize_colors(hex_rgb_colors))
        return normalized_to_hex_colors

    def init(self):
        if not exists(COLORIZED_PATH):
            mkdir(COLORIZED_PATH)
        else:
            rm(COLORIZED_PATH)
            mkdir(COLORIZED_PATH)

        self.view.set_syntax_file("Packages/CSS/CSS.tmLanguage")


# class CssColorsRollback(sublime_plugin.EventListener):
    # def on_

WEB_COLORS = {
    "White": "#FFFFFF",
    "Silver": "#C0C0C0",
    "Gray": "#808080",
    "Black": "#000000",
    "Red": "#FF0000",
    "Maroon": "#800000",
    "Yellow": "#FFFF00",
    "Olive": "#808000",
    "Lime": "#00FF00",
    "Green": "#008000",
    "Aqua": "#00FFFF",
    "Teal": "#008080",
    "Blue": "#0000FF",
    "Navy": "#000080",
    "Fuchsia": "#FF00FF",
    "Purple": "#800080"}

# %s = color hex code without # prefix
syntax_color_template = """
                <dict>
                    <key>captures</key>
                    <dict>
                        <key>1</key>
                        <dict>
                            <key>name</key>
                            <string>punctuation.definition.constant.css</string>
                        </dict>
                    </dict>
                    <key>match</key>
                    <string>{0}</string>
                    <key>name</key>
                    <string>{1}.css-colorize.css</string>
                </dict>
"""
template = """
        <key>facepalm-values</key>
        <dict>
            <key>patterns</key>
            <array>
                {0}
            </array>
        </dict>
"""
include = """
<dict>
    <key>include</key>
    <string>#facepalm-values</string>
</dict>
"""


def normalize_colors(colors):
    # convert [colors] to hex
    # [colors]: hex or rgb
    normalized_colors = []
    for color in colors:
        if color.title() in WEB_COLORS:
            hex_color = WEB_COLORS[color.title()]
            match_rule = "(%s)\\b" % color
        elif not color.startswith('#'):
            hex_color = rgb_to_hex(tuple(color.split(',')))
            match_rule = "(rgb)(\(%s\))(?x)" % color
        else:
            hex_color = color
            match_rule = "(#)(%s)\\b" % color[1:]
        normalized_colors.append((hex_color, match_rule))
    return normalized_colors


def rgb_to_hex(rgb):
    # rgb: tuple of r,g,b values
    return '#%02x%02x%02x' % tuple(int(x) for x in rgb)


def add_scopes(scopes):
    """
    Add given scopes to syntax file, sufixed by 'css-colorize.css'
    """

    scopes_xml = [syntax_color_template.format(scope[1], scope[0][1:]) for scope in scopes]
    return template.format('\n'.join(scopes_xml)).split()


def generate_syntax(view, color_codes):

    with open(join(PACKAGES_PATH, 'CSS/CSS.tmLanguage')) as syn_file:
        syn_file_content = syn_file.readlines()
        new_rules = add_scopes(color_codes)
        colorized = syn_file_content[0:553] + include.split() + syn_file_content[553:]
        colorized = colorized[0:537] + new_rules + colorized[537:]

    # write new color rules to newly crated syntax file
    with open(join(COLORIZED_PATH, "CSS-colorized.tmLanguage"), 'w') as syntax_f:
        syntax_f.write(''.join(colorized))

    view.set_syntax_file(join(COLORIZED_PATH, "CSS-colorized.tmLanguage"))


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


theme_templ = """
    <dict>
        <key>name</key>
        <string>\'{0}\'</string>
        <key>scope</key>
        <string>{0}.css-colorize.css</string>
        <key>settings</key>
        <dict>
            <key>background</key>
            <string>{1}</string>
            <key>foreground</key>
            <string>{2}</string>
        </dict>
    </dict>
"""


def opposite(hex_color):
    opp_int = 16777215 - int(hex_color[1:], 16)
    opp_hex = hex(opp_int)
    return "#" + opp_hex[0] + opp_hex[2:]


def add_colors(colors):
    """
    Add given scopes to syntax file, sufixed by 'css-colorize.css'
    """
    colors_xml = [theme_templ.format(color[0][1:], color[0], opposite(color[0])) for color in colors]
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
        colorized_theme = theme_content[0:1863] + new_colores + theme_content[1863:]

    with open(join(COLORIZED_PATH, 'Colorized-' + theme), 'w') as f:
        f.write(''.join(colorized_theme))

    set_current_theme(join(COLORIZED_PATH, 'Colorized-' + theme))
