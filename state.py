import sublime

from settings import Settings

in_memory_settings = Settings('Colorized.sublime-settings')


class State(object):

    def __init__(self, colors, file_id):
        self._settings = sublime.load_settings('Colorized.sublime-settings')
        self.colors = colors
        self.file_id = file_id

    def save(self):
        state = {self.file_id: {'colors': [str(x) for x in self.colors]}}
        self._settings.set('state', state)

    @property
    def need_generate_new_color_file(self):
        saved_colors = self.saved_state['colors']
        if set(self.colors) - set(saved_colors):
            return True

    @property
    def saved_state(self):
        """Returns saved colors if any
        or empty state
        """

        s = self._settings.get('state')
        if not s or not s.get(self.file_id):
            return {'colors': []}
        return s[self.file_id]

    def erase(self):
        s = self._settings.get('state')
        if s:
            self._settings.erase('state')