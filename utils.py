from os.path import join as joinpath
from os.path import exists, abspath
import os


# Taken from sublime-git
PLUGIN_DIRECTORY = abspath(os.curdir.replace(os.path.normpath(
                   os.path.join(os.getcwd(), '..', '..')) + os.path.sep, '').\
                   replace(os.path.sep, '/'))
MENU_FILE = joinpath(PLUGIN_DIRECTORY, "Main.sublime-menu")


def on_off(b):
    return "off" if b else "on"


def menu(l, g):
    menu = """
    [
    { "id": "view",
    "children":
    [
        {
            "caption": "live css colorizing",
            "children":
            [
            {"caption": "turn %s for this file",
            "command": "toggle_auto_css_colorize"},
            {"caption": "turn %s globaly",
            "command": "toggle_auto_css_colorize",
            "checkbox": true}
            ]
        }
    ]
    }
    ]
    """ % (on_off(l), on_off(g))
    return menu


def write_menu(text):
    with open(MENU_FILE, 'w') as m:
        m.write(text)


def generate_menu(l, g):
    # user_settings = Settings('CSS-colors.sublime-settings')
    # state = user_settings.dynamic_highlight
    menu_content = menu(l, g)
    write_menu(menu_content)


def rm_menu():
    if exists(MENU_FILE):
        os.remove(MENU_FILE)
