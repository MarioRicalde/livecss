import sublime_plugin

# local imports
from livecss.colorizer import *
from livecss.utils import *
from livecss.file_operatios import clean_junk
from livecss.config import Config
from livecss.state import State
from livecss.theme import theme

from livecss.debug import log


class CssColorizeCommand(sublime_plugin.TextCommand):
    def run(self, edit, erase_state=False):
        colorize_file(self.view, erase_state)


class CssUncolorizeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        uncolorize_file(self.view)


class EventManager(sublime_plugin.EventListener):
    def __init__(self):
        # before anything
        # theme.set(theme.uncolorized_path)
        clean_junk()
        # print "settings", uncolorized_path

    def on_load(self, view):
        theme.on_select_new_theme(lambda: selected_new_theme(view))
        if need_colorization(view):
            colorize_file(view, True)

    def on_close(self, view):
        uncolorize_file(view)

    def on_modified(self, view):
        if need_colorization(view):
            colorize_file(view)

    def on_activated(self, view):
        if file_is_css(view):
            log("on_activated was called")
            generate_menu(view)

            # set file's own theme path
            # because we use one per css file
            state = State(view)
            if state.theme_path:
                theme.set(state.theme_path)

        if need_colorization(view):
            colorize_file(view)

        if need_uncolorization(view):
            uncolorize_file(view)


class ToggleLocalLiveCss(sublime_plugin.TextCommand):
    def run(self, edit):
        state = Config(file_id(self.view)).local_on
        if state:
            uncolorize_file(self.view)
        else:
            colorize_file(self.view, True)

        Config(file_id(self.view)).local_on = not state
        generate_menu(self.view)

    def is_visible(self):
        return file_is_css(self.view)


class ToggleGlobalLiveCss(sublime_plugin.TextCommand):
    def run(self, edit):
        state = Config(file_id(self.view))

        if state.global_on:
            uncolorize_file(self.view)
            Config(file_id(self.view)).local_on = not state.global_on
        else:
            if state.local_on:
                colorize_file(self.view, True)

        Config(file_id(self.view)).global_on = not state.global_on
        generate_menu(self.view)

    def is_visible(self):
        return file_is_css(self.view)
