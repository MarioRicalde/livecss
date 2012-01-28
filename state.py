import sublime

# from theme import theme
# from debug import log


class State(object):
    """ Wrapper around sublime settings
        dump not _properties of children to st settings obj
    """

    def __init__(self, file_id, colors=False):
        self._colors = colors or []
        self._file_id = str(file_id)
        self._settings = sublime.load_settings('in_memory_settings')
        if not self._settings.get(self._file_id):
            self._settings.set(self._file_id, {})
        self.global_live_css = False

    def __getattribute__(self, attr):
        if not attr.startswith("_"):
            s = self._settings.get(self._file_id)
            return s.get(attr)

        return object.__getattribute__(self, attr)

    def __setattr__(self, attr, value):
        object.__setattr__(self, attr, value)
        if not attr.startswith("_"):
            s = self._settings.get(self._file_id)
            s[attr] = value
            self._settings.set(self._file_id, s)


def need_generate_new_color_file(state):
    if set(state._colors) - set(state.colors or []):
        generate = True
    else:
        generate = False
    state.colors = [str(x) for x in state._colors]
    return generate


def erase(state):
   state._settings.set(state._file_id, {})