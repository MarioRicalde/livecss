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


def menu_template(lstate, gstate):
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
            {"caption": "turn %s globally",
            "command": "toggle_auto_css_colorize"}
            ]
        }
    ]
    }
    ]
    """ % (on_off(lstate), on_off(gstate))
    return menu


def write_menu(string):
    with open(MENU_FILE, 'w') as m:
        m.write(string)


def generate_menu(lstate, gstate):
    """ Writes Main.sublime-menu file to package directory"""
    menu_content = menu_template(lstate, gstate)
    write_menu(menu_content)


def rm_menu():
    """ Deletes Main.sublime-menu file from package directory"""
    if exists(MENU_FILE):
        os.remove(MENU_FILE)
