# sublime
import sublime_plugin

# local imports
# from debug import log

from lib.colorizer import *


class CssColorizeCommand(sublime_plugin.TextCommand):
    def run(self, edit, erase_state=False):
        colorize_file(self.view, erase_state)


class CssUncolorizeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        uncolorize_file(self.view)


# class EventManager(sublime_plugin.EventListener):
#     # def __init__(self):
#     #     # on plugin load
#     #     clean_themes_folder()

#     def on_load(self, view):
#         # clean!!!, set theme to uncolorized if necessary

#         # theme.on_select_new_theme(lambda: colorize_if_not(view))
#         generate_menu(view)
#         if need_colorization(view):
#             log("Loading")
#             colorize_file(view, True)

#     def on_modified(self, view):
#         if need_colorization(view):
#             log("On on_modified")
#             colorize_file(view)

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


# class ToggleLocalLiveCss(sublime_plugin.TextCommand):
#     def run(self, edit):
#         state = Config(file_id(self.view)).local_on
#         log("State ", str(state))
#         if state:
#             log("Running uncolorizing")
#             self.view.window().run_command('css_uncolorize')
#         else:
#             log("Running colorizing")
#             # self.view.window().run_command('css_colorize', {'erase_state': True})
#             colorize_file(self.view, True)

#         setattr(Config(file_id(self.view)), 'local_on', not state)
#         generate_menu(self.view)

#     def is_visible(self):
#         return file_is_css(self.view)


# class ToggleGlobalLiveCss(sublime_plugin.TextCommand):
#     def run(self, edit):
#         state = Config(file_id(self.view)).global_on

#         if state:
#             # global uncolorizing
#             self.view.window().run_command('css_uncolorize')
#         else:
#             # self.view.window().run_command('css_colorize', {'erase_state': True})
#             colorize_file(self.view, True)

#         setattr(Config(file_id(self.view)), 'global_on', not state)
#         generate_menu(self.view)

#     def is_enabled(self):
#         return file_is_css(self.view)
