from shutil import copyfile
from os.path import join
import sublime
import sublime_plugin


#alg:
# select all colors:
# rgb and named colors to hex form
# rewrite CSS.tmLanguage file with rules for each color
#   save it by a different name, in order to ST cat regenerate rules properly
#   before exit roll it back
# rewrite $current_theme.tmTheme file with new color difinisions
# reapply sytntax and theme files

class CssColorsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.set_syntax_file("Packages/CSS/CSS.tmLanguage")
        colors_by_names = self.view.find_by_selector("3bbfce.css-colorize.css")
        colors_by_rgb = self.view.find_by_selector("constant.other.color.rgb-value.css")
        colors_by_hex = self.view.find_by_selector("support.constant.color.w3c-standard-color-name.css")
        print [self.view.substr(color) for color in colors_by_names + colors_by_hex]

# %s1 color code without leading # char, %s2 color code
theme_template = """<dict>
                    <key>name</key>
                    <string>css-colorize</string>
                    <key>scope</key>
                    <string>%s</string>
                    <key>settings</key>
                    <dict>
                        <key>foreground</key>
                        <string>%s</string>
                    </dict>
        </dict>"""

# %s = syntax rule for one color
synax_genral = """
    <key>facepalm-values</key>
        <dict>
            <key>patterns</key>
            %s
        </dict>
"""
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
        <string>(#)(%s)\b</string>
        <key>name</key>
        <string>%s.css-colorize.css</string>
    </dict>
"""
sytax_rule_template = synax_genral % syntax_color_template % color


def generate_syntax(color_codes):
    """Generate new css syntax with `color_code`,
    #Args:
    color_codes: list of str
    """

    rules = [syntax_color_template % color_code.split('#')[-1]  for color_code in color_codes]
    with open('"Packages/CSS/CSS.tmLanguage') as syn_file:
        syn_file_content = syn_file.read()
    css_dir_path = join(self.view.packages_path(), "CSS")

    # copy css synatax file
    copyfile(join(css_dir_path, "CSS.tmLanguage"), join(css_dir_path, "CSS-colorized.tmLanguage"))
    # write new color rules to newly crated syntax file
    with open join(css_dir_path, "CSS-colorized.tmLanguage") as syntax_f:
        pass


def generate_theme(color_code):
    rules = theme_template % (color_code.split('#')[-1], color_code)
    # check if we can apply colorsheme just of updating current color file
    # or we have to copy it like syn file
    # code

