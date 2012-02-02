from wrappers import PerFileConfig


class State(PerFileConfig):
    def __init__(self, id, colors=False):
        super(State, self).__init__(id=id,
                                    settings_file='temp',
                                    in_memory=True,
                                    ignored_props=('need_generate_theme_file', 'erase'))
        self._colors = colors or []

    @property
    def need_generate_theme_file(self):
        if set(self._colors) - set(self.colors or []):
            generate = True
        else:
            generate = False
        self.colors = [str(x) for x in self._colors]
        return generate

    def erase(self):
        self._s[self._id] = {}
