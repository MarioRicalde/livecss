import sublime

# local imports
from helpers import AvailabilityChecker


class Settings(object):

    """ Wrapper around sublime settings,
    which uses ST settings to store instance properties

    """

    def __init__(self, settings_file, in_memory):
        """
        @param {str} settings_file: settings file name
        @param {bool} in_memory: save on each attribute setting

        """
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

    def __contains__(self, attr):
        if not getattr(self, attr) == None:
            return True

    def __getitem__(self, attr):
        return getattr(self, attr)

    def __setitem__(self, attr, value):
        setattr(self, attr, value)

    def _save(self):
        sublime.save_settings(self._settings_file)


class PerFileConfig(object):
    """ Allows to store instance properties in per id base

    """

    def __init__(self, id, settings_file, in_memory, ignored_attrs=False):
        """
        @param {anytype} id: identification sign
        @param {str} settings_file: settings file name
        @param {bool} in_memory: save on each attribute setting
        @param {anytype} ignored_attrs: attribute to ignore

        """

        self._id = str(id)
        self._ignored_attrs = AvailabilityChecker(ignored_attrs)
        self._s = Settings(settings_file, in_memory)

        if self._id not in self._s:
            self._s[self._id] = {}

    def __getattribute__(self, attr):
        """Retrieve attribute from ST settings.
        Ignore underscored and those in ignored_attrs.

        """

        if attr.startswith("_"):
            return object.__getattribute__(self, attr)
        if attr not in self._ignored_attrs:
            return self._s[self._id].get(attr)
        else:
            return object.__getattribute__(self, attr)

    def __setattr__(self, attr, value):
        """Always uses standard attribute setter
        If it's not underscored or found as ignored,
        it stores in ST settings

        """

        object.__setattr__(self, attr, value)
        if not attr.startswith("_"):
            if not attr in self._ignored_attrs:
                s = self._s[self._id]
                s[attr] = value
                self._s[self._id] = s
