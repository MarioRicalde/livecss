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
