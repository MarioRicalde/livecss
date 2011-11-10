from os.path import join, exists, basename
from os import mkdir
import sublime
import sublime_plugin
from shutil import rmtree as rm


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
            print "Not changed"
            return
        self.init()
        save_colors_hash(colors)
        generate_syntax(self.view, colors)
        highlight(colors)

    def colors_in_current_file(self):
        w3c_colors = self.view.find_by_selector("support.constant.color.w3c-standard-color-name.css")
        extra_web_colors = self.view.find_by_selector("invalid.deprecated.color.w3c-non-standard-color-name.css")
        hex_rgb_regions = self.view.find_by_selector("constant.other.color.rgb-value.css")
        hex_rgb_colors = [self.view.substr(color) for color in hex_rgb_regions + w3c_colors + extra_web_colors]
        normalized_to_hex_colors = set(normalize_colors(hex_rgb_colors))
        return normalized_to_hex_colors

    def init(self):
        if not exists(COLORIZED_PATH):
            mkdir(COLORIZED_PATH)
        else:
            rm(COLORIZED_PATH)
            mkdir(COLORIZED_PATH)

    def apply_colorized_syntax(self):
        self.view.set_syntax_file(COLORIZED_PATH + "Colorized-CSS.tmLanguage")

    def apply_original_syntax(self):
        self.view.set_syntax_file("Packages/CSS/CSS.tmLanguage")


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

WEB_EXTRA_COLORS = {
'AliceBlue'            : '#F0F8FF',
'AntiqueWhite'         : '#FAEBD7',
'Aquamarine'           : '#7FFFD4',
'Azure'                : '#F0FFFF',
'Beige'                : '#F5F5DC',
'Bisque'               : '#FFE4C4',
'BlanchedAlmond'       : '#FFEBCD',
'BlueViolet'           : '#8A2BE2',
'Brown'                : '#A52A2A',
'BurlyWood'            : '#DEB887',
'CadetBlue'            : '#5F9EA0',
'Chartreuse'           : '#7FFF00',
'Chocolate'            : '#D2691E',
'Coral'                : '#FF7F50',
'CornflowerBlue'       : '#6495ED',
'Cornsilk'             : '#FFF8DC',
'Crimson'              : '#DC143C',
'Cyan'                 : '#00FFFF',
'DarkBlue'             : '#00008B',
'DarkCyan'             : '#008B8B',
'DarkGoldenRod'        : '#B8860B',
'DarkGray'             : '#A9A9A9',
'DarkGrey'             : '#A9A9A9',
'DarkGreen'            : '#006400',
'DarkKhaki'            : '#BDB76B',
'DarkMagenta'          : '#8B008B',
'DarkOliveGreen'       : '#556B2F',
'Darkorange'           : '#FF8C00',
'DarkOrchid'           : '#9932CC',
'DarkRed'              : '#8B0000',
'DarkSalmon'           : '#E9967A',
'DarkSeaGreen'         : '#8FBC8F',
'DarkSlateBlue'        : '#483D8B',
'DarkSlateGray'        : '#2F4F4F',
'DarkSlateGrey'        : '#2F4F4F',
'DarkTurquoise'        : '#00CED1',
'DarkViolet'           : '#9400D3',
'DeepPink'             : '#FF1493',
'DeepSkyBlue'          : '#00BFFF',
'DimGray'              : '#696969',
'DimGrey'              : '#696969',
'DodgerBlue'           : '#1E90FF',
'FireBrick'            : '#B22222',
'FloralWhite'          : '#FFFAF0',
'ForestGreen'          : '#228B22',
'Gainsboro'            : '#DCDCDC',
'GhostWhite'           : '#F8F8FF',
'Gold'                 : '#FFD700',
'GoldenRod'            : '#DAA520',
'Grey'                 : '#808080',
'GreenYellow'          : '#ADFF2F',
'HoneyDew'             : '#F0FFF0',
'HotPink'              : '#FF69B4',
'IndianRed'            : '#CD5C5C',
'Indigo'               : '#4B0082',
'Ivory'                : '#FFFFF0',
'Khaki'                : '#F0E68C',
'Lavender'             : '#E6E6FA',
'LavenderBlush'        : '#FFF0F5',
'LawnGreen'            : '#7CFC00',
'LemonChiffon'         : '#FFFACD',
'LightBlue'            : '#ADD8E6',
'LightCoral'           : '#F08080',
'LightCyan'            : '#E0FFFF',
'LightGoldenRodYellow' : '#FAFAD2',
'LightGray'            : '#D3D3D3',
'LightGrey'            : '#D3D3D3',
'LightGreen'           : '#90EE90',
'LightPink'            : '#FFB6C1',
'LightSalmon'          : '#FFA07A',
'LightSeaGreen'        : '#20B2AA',
'LightSkyBlue'         : '#87CEFA',
'LightSlateGray'       : '#778899',
'LightSlateGrey'       : '#778899',
'LightSteelBlue'       : '#B0C4DE',
'LightYellow'          : '#FFFFE0',
'LimeGreen'            : '#32CD32',
'Linen'                : '#FAF0E6',
'Magenta'              : '#FF00FF',
'MediumAquaMarine'     : '#66CDAA',
'MediumBlue'           : '#0000CD',
'MediumOrchid'         : '#BA55D3',
'MediumPurple'         : '#9370D8',
'MediumSeaGreen'       : '#3CB371',
'MediumSlateBlue'      : '#7B68EE',
'MediumSpringGreen'    : '#00FA9A',
'MediumTurquoise'      : '#48D1CC',
'MediumVioletRed'      : '#C71585',
'MidnightBlue'         : '#191970',
'MintCream'            : '#F5FFFA',
'MistyRose'            : '#FFE4E1',
'Moccasin'             : '#FFE4B5',
'NavajoWhite'          : '#FFDEAD',
'OldLace'              : '#FDF5E6',
'OliveDrab'            : '#6B8E23',
'OrangeRed'            : '#FF4500',
'Orchid'               : '#DA70D6',
'PaleGoldenRod'        : '#EEE8AA',
'PaleGreen'            : '#98FB98',
'PaleTurquoise'        : '#AFEEEE',
'PaleVioletRed'        : '#D87093',
'PapayaWhip'           : '#FFEFD5',
'PeachPuff'            : '#FFDAB9',
'Peru'                 : '#CD853F',
'Pink'                 : '#FFC0CB',
'Plum'                 : '#DDA0DD',
'PowderBlue'           : '#B0E0E6',
'RosyBrown'            : '#BC8F8F',
'RoyalBlue'            : '#4169E1',
'SaddleBrown'          : '#8B4513',
'Salmon'               : '#FA8072',
'SandyBrown'           : '#F4A460',
'SeaGreen'             : '#2E8B57',
'SeaShell'             : '#FFF5EE',
'Sienna'               : '#A0522D',
'SkyBlue'              : '#87CEEB',
'SlateBlue'            : '#6A5ACD',
'SlateGray'            : '#708090',
'SlateGrey'            : '#708090',
'Snow'                 : '#FFFAFA',
'SpringGreen'          : '#00FF7F',
'SteelBlue'            : '#4682B4',
'Tan'                  : '#D2B48C',
'Thistle'              : '#D8BFD8',
'Tomato'               : '#FF6347',
'Turquoise'            : '#40E0D0',
'Violet'               : '#EE82EE',
'Wheat'                : '#F5DEB3',
'WhiteSmoke'           : '#F5F5F5',
'YellowGreen'          : '#9ACD32'}



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


def normalize_colors(colors):
    # convert [colors] to hex
    # [colors]: hex or rgb
    normalized_colors = []
    for color in colors:
        WEB_COLORS.update(WEB_EXTRA_COLORS)
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
        colorized_theme = theme_content[0:8] + new_colores + theme_content[8:]
        # colorized_theme = theme_content[0:1863] + new_colores + theme_content[1863:]

    with open(join(COLORIZED_PATH, 'Colorized-' + theme), 'w') as f:
        f.write(''.join(colorized_theme))

    set_current_theme(join(COLORIZED_PATH, 'Colorized-' + theme))
