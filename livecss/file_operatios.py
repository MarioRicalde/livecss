from os import listdir
from os import remove as rm
from os.path import exists, join
import sublime


def clean_junk():
    theme_dir = join(sublime.packages_path(), 'Color Scheme - Default')
    old_themes = [f for f in listdir(theme_dir) if f.startswith('Colorized-')]
    for old_theme in old_themes:
        rm_theme(join(theme_dir, old_theme))


def rm_if_exists(path):
    if exists(path):
        rm(path)


def rm_theme(path):
    if path:
        rm_if_exists(path)
        rm_if_exists(path + '.cache')
