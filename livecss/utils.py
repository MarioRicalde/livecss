from config import Config
from state import State
from theme import theme
from colorizer import colorize_file
from menu import create_menu

from os.path import join, dirname, basename


def generate_menu(view):
    config = Config(file_id(view))
    global_opt = config.global_on
    local_opt = config.local_on
    create_menu(local_opt, global_opt)


def file_id(view):
    return view.file_name() or view.buffer_id()


def file_is_css(view):
    point = view.sel()[0].begin()
    file_scope = view.scope_name(point).split()[0]
    if file_scope == 'source.css':
        return True


def need_colorization(view):
    # document the flow
    if not file_is_css(view):
        return

    config = Config(file_id(view))
    global_on = config.global_on
    local_on = config.local_on
    if not local_on:
        return
    if global_on:
        return True


def need_uncolorization(view):
    # document the flow
    if not file_is_css(view):
        return

    config = Config(file_id(view))
    global_on = config.global_on
    if not global_on:
        return True
