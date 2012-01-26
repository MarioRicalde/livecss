from os.path import join as joinpath
from os.path import abspath
from os import curdir

from settings import Settings

PLUGIN_PATH = abspath(curdir)


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
    with open(joinpath(PLUGIN_PATH, "Main.sublime-menu"), 'w') as m:
        m.write(text)


def generate_menu():
    user_settings = Settings('CSS-colors.sublime-settings')
    state = user_settings.dynamic_highlight
    menu_content = menu(state)
    write_menu(menu_content)


