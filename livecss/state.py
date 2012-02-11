from wrappers import PerFileConfig


class State(PerFileConfig):
    def __init__(self, view, colors=False, regions=False):
        super(State, self).__init__(id=view.buffer_id(),
                                    settings_file='temp',
                                    in_memory=True,
                                    ignored_attrs=('need_generate_theme_file', 'erase', 'is_dirty'))
        self._view = view
        self._colors = colors or []
        self._regions = regions or []

    @property
    def is_dirty(self):
        # if we don't have previously saved state
        if not self.regions:
            is_dirty = True

        old_regions = get_highlighted_regions(self._view, self.count)
        new_regions = self._regions

        if old_regions == new_regions:
            is_dirty = False
        else:
            is_dirty = True

        self.regions = self._regions
        return is_dirty

    @property
    def need_generate_theme_file(self):
        if set(self._colors) - set(self.colors or []):
            need_generate = True
        else:
            need_generate = False
        self.colors = [str(x) for x in self._colors]
        return need_generate

    def erase(self):
        self._s[self._id] = {}


def get_highlighted_regions(view, last_highlighted_region):
    """ Returns currently highlighted regions
    """
    if not last_highlighted_region:
        return
    regions = []
    for i in range(int(last_highlighted_region)):
        region = view.get_regions('css_color_%d' % i)
        if region:
            regions.append(region[0])
    return regions
