from menu import create_menu
from os import remove as rm
from os.path import exists
from config import Config


def generate_menu(view):
    config = Config(file_id(view))
    global_opt = config.global_on
    local_opt = config.local_on
    create_menu(local_opt, global_opt)


def file_id(view):
    return view.file_name() or view.buffer_id()


def file_is_css(view):
    any_point = view.sel()[0].begin()
    file_scope = view.scope_name(any_point).split()[0]
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


def rm_if_exists(path):
    if exists(path):
        rm(path)

escape = lambda s: "\'" + s + "\'"
