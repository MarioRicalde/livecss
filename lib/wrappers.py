import sublime


class Settings(object):

    """ Wrapper around sublime settings """

    def __init__(self, settings_file, in_memory):
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

make_eq = lambda x: lambda y: x == y


class Props(object):
    def __init__(self, callbacks):
        if not isinstance(callbacks, list) or \
           not isinstance(callbacks, tuple):
            callbacks = tuple(callbacks)

        self._callbacks = []
        for cb in callbacks:
            if not callable(cb):
                self._callbacks.append(make_eq(cb))
            else:
                self._callbacks.append(cb)

    def __contains__(self, attr):
        return any(cb(attr) for cb in self._callbacks)


class PerFileConfig(object):
    """ Save on each property change """
    def __init__(self, id, settings_file, in_memory, ignored_props=False):
        self._id = str(id)
        self._ignored_props = Props(ignored_props)
        self._s = Settings(settings_file, in_memory)

        if self._id not in self._s:
            self._s[self._id] = {}

    def __getattribute__(self, attr):
        if attr.startswith("_"):
            return object.__getattribute__(self, attr)
        if attr not in self._ignored_props:
            return self._s[self._id].get(attr)
        else:
            return object.__getattribute__(self, attr)

    def __setattr__(self, attr, value):
        object.__setattr__(self, attr, value)
        if not attr.startswith("_"):
            if not attr in self._ignored_props:
                s = self._s[self._id]
                s[attr] = value
                self._s[self._id] = s
