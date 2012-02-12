from os.path import join as joinpath
from os.path import abspath
import os

import sublime

# Taken from sublime-git
PLUGIN_DIRECTORY = abspath(os.curdir.replace(os.path.normpath(
                   os.path.join(os.getcwd(), '..', '..')) + os.path.sep, '').\
                   replace(os.path.sep, '/'))
MENU_FILE = joinpath(PLUGIN_DIRECTORY, "Main.sublime-menu")
OS = sublime.platform()


def on_off(b):
    return "off" if b else "on"


def menu_template(lstate, gstate):
    menu = """
    [
        {
            "id": "view",
            "children":
            [
                {
                    "caption": "live css colorizing",
                    "children":
                    [
                    {"caption": "turn %s for this file",
                    "command": "toggle_local_live_css"},
                    {"caption": "turn %s globally",
                    "command": "toggle_global_live_css"}
                    ]
                }
            ]
        }
    ]
    """ % (on_off(lstate), on_off(gstate))
    return menu


def menu_template_for_linux():
    menu = """
    [
        {
            "id": "view",
            "children":
            [
                {
                    "caption": "live css colorizing",
                    "children":
                    [
                    {"caption": "Toggle livecss locally",
                    "command": "toggle_local_live_css"},
                    {"caption": "Toggle livecss globally",
                    "command": "toggle_global_live_css"}
                    ]
                }
            ]
        }
    ]
    """
    return menu


def write_menu(string):
    with open(MENU_FILE, 'w') as m:
        m.write(string)

#TODO: better name
def create_menu(lstate, gstate):
    """ Writes Main.sublime-menu file to package directory"""
    print OS
    if OS == 'linux':
        menu_content = menu_template_for_linux
    else:
        menu_content = menu_template(lstate, gstate)
    write_menu(menu_content)
