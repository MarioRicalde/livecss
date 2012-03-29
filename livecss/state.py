"""
    livecss.state
    ~~~~~~~~~

    This module implements state object and function to associate state with view

"""

class State(object):
    def __init__(self, view):
        self.count = 0
        self.theme_path = ""
        self.saved_colors = []
        self.saved_regions = []
        self.view = view

    @property
    def is_dirty(self):
        """Indicates if state was changed"""

        # if we don't have previously saved state
        if not self.regions:
            return

        highlighted_regions = get_highlighted_regions(self.view, self.count)

        # check if regions have changed
        if highlighted_regions == self.regions:
            is_dirty = False
        else:
            is_dirty = True

        # check if length of region's changed
        if is_dirty is False:
            for reg_pair in zip(self.saved_regions, self.regions):
                if abs(reg_pair[0].a - reg_pair[0].b) != abs(reg_pair[1].a - reg_pair[1].b):
                    is_dirty = True

        # save current regions
        self.saved_regions = self.regions
        return is_dirty

    @property
    def need_generate_theme_file(self):
        """Indicates if new color definition appeared in current file"""

        # check if there are new colors in view
        if set(self.colors) - set(self.saved_colors):
            need_generate = True
        else:
            need_generate = False

        # save current colors
        self.saved_colors = self.colors
        return need_generate

    def erase(self):
        self.colors = []
        self.regions = []


def get_highlighted_regions(view, last_highlighted_region):
    """Return currently highlighted regions for this file."""

    if not last_highlighted_region:
        return
    regions = []
    for i in range(int(last_highlighted_region)):
        region = view.get_regions('css_color_%d' % i)
        if region:
            regions.append(region[0])
    return regions


states = dict()
def state_for(view):
    if view.buffer_id() not in states:
        states[view.buffer_id()] = State(view)
    return states[view.buffer_id()]
