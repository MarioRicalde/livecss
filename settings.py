import sublime


class Settings(object):
    """ Wrapper around sublime settings"""

    def __init__(self, settings_file, in_memory=False):
        self._in_memory = in_memory
        self._settings_file = settings_file
        self._settings = sublime.load_settings(settings_file)

    def __getattribute__(self, attr):
        if not attr.startswith("_"):
            return self._settings.get(attr)

        return object.__getattribute__(self, attr)

    def __setattr__(self, attr, value):
        object.__setattr__(self, attr, value)
        if not attr.startswith("_"):
            self._settings.set(attr, value)
            if not self._in_memory:
                self._save()

    def _save(self):
        sublime.save_settings(self._settings_file)