import sublime_plugin

# local imports
from livecss.colorizer import *
from livecss.config import Config
from livecss.file_operatios import clean_junk
from livecss.state import State
from livecss.theme import theme
from livecss.utils import need_colorization, need_uncolorization, fils_is_colorizable, generate_menu, colorize_on_select_new_theme


class CssColorizeCommand(sublime_plugin.TextCommand):
    def run(self, edit, erase_state=False):
        colorize_file(self.view, erase_state)


class CssUncolorizeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        uncolorize_file(self.view)


class EventManager(sublime_plugin.EventListener):
    def __init__(self):
        # before anything
        clean_junk()

    def on_load(self, view):
        # set hook to recolorize if different theme was chosen
        theme.on_select_new_theme(lambda: colorize_on_select_new_theme(view))

        if need_colorization(view):
            colorize_file(view, True)

    def on_close(self, view):
        uncolorize_file(view)

    def on_modified(self, view):
        if need_colorization(view):
            colorize_file(view)

    def on_activated(self, view):
        if fils_is_colorizable(view):
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


class ToggleLocalLiveCssCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        state = Config(self.view).local_on
        if state:
            uncolorize_file(self.view)
        else:
            colorize_file(self.view, True)

        Config(self.view).local_on = not state
        generate_menu(self.view)

    def is_visible(self):
        return fils_is_colorizable(self.view)


class ToggleGlobalLiveCssCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        state = Config(self.view)

        if state.global_on:
            uncolorize_file(self.view)
            Config(self.view).local_on = not state.global_on
        else:
            if state.local_on:
                colorize_file(self.view, True)

        Config(self.view).global_on = not state.global_on
        generate_menu(self.view)

    def is_visible(self):
        return fils_is_colorizable(self.view)
