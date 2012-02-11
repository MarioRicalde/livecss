# sublime
import sublime_plugin

# local imports
# from debug import log

from livecss.colorizer import *
from livecss.utils import *
from livecss.config import Config


class CssColorizeCommand(sublime_plugin.TextCommand):
    def run(self, edit, erase_state=False):
        colorize_file(self.view, erase_state)


class CssUncolorizeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        uncolorize_file(self.view)


class EventManager(sublime_plugin.EventListener):
#     # def __init__(self):
#     #     # on plugin load
#     #     clean_themes_folder()

#     def on_load(self, view):
# #         # clean!!!, set theme to uncolorized if necessary

# #         # theme.on_select_new_theme(lambda: colorize_if_not(view))
#         generate_menu(view)
#         if need_colorization(view):
#             colorize_file(view, True)

    def on_close(self, view):
        uncolorize_file(view)

    def on_modified(self, view):
        if need_colorization(view):
            colorize_file(view)

#     # def on_activated(self, view):
#     #     """Creates menu on gaining focus"""
#     #     # generate_menu(view)
#     #     if need_colorization(view):
#     #         colorize_file(view)
#     #         log("on_activated")

#     # def on_deactivated(self, view):
#         # """Destroys menu on focus lost"""
#         # read as if prev file is css
#         # if file_is_css(view):
#             # log('on_deactivated')
#             # rm_menu()

# Make it more robust
class ToggleLocalLiveCss(sublime_plugin.TextCommand):
    def run(self, edit):
        state = Config(file_id(self.view)).local_on
        if state:
            self.view.window().run_command('css_uncolorize')
        else:
            colorize_file(self.view, True)

        setattr(Config(file_id(self.view)), 'local_on', not state)
        generate_menu(self.view)

    def is_visible(self):
        return file_is_css(self.view)


class ToggleGlobalLiveCss(sublime_plugin.TextCommand):
    def run(self, edit):
        state = Config(file_id(self.view))

        if state.global_on:
            if state.local_on:
                self.view.window().run_command('css_uncolorize')
        else:
            colorize_file(self.view, True)

        setattr(Config(file_id(self.view)), 'global_on', not state.global_on)
        generate_menu(self.view)

    def is_enabled(self):
        return file_is_css(self.view)
