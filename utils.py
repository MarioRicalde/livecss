from os.path import join as joinpath
from os.path import abspath, exists
from os import curdir, remove

from settings import Settings

PLUGIN_PATH = abspath(curdir)
MENU_FILE = joinpath(PLUGIN_PATH, "Main.sublime-menu")


def on_off(b):
    val = "off" if b else "on"
    return val


def menu(state):
    menu = """
    [
        {
            "id": "view",
            "children":
            [
                {
                    "caption": "turn css dynamic highligting %s",
                    "command": "toggle_auto_css_colorize"
                }
                ]
            }
    ]
    """ % on_off(state)
    return menu


def write_menu(text):
    with open(MENU_FILE, 'w') as m:
        m.write(text)


def generate_menu():
    user_settings = Settings('CSS-colors.sublime-settings')
    state = user_settings.dynamic_highlight
    menu_content = menu(state)
    write_menu(menu_content)


def rm_menu():
    if exists(MENU_FILE):
        remove(MENU_FILE)
