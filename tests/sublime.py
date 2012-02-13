"""

    Fake sublime module

"""


def packages_path():
    return "/Users/ask/Library/Application Support/Sublime Text 2/Packages"

def platform():
    return 'osx'

def load_settings(name):
    return

class Region:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def begin(self):
        return min(self.a, self.b)

    def end(self):
        return max(self.a, self.b)

    def empty(self):
        return self.begin() == self.end()

    def __eq__(self, another):
        return (self.a, self.b) == (another.a, another.b)

    def __repr__(self):
        return str((self.a, self.b))


class RegionSet:
    def __init__(self, region):
        self.regions = []
        self.add(region)

    def add(self, region):
        if region not in self.regions:
            self.regions.append(region)

    def clear(self):
        self.regions = []

    def __getitem__(self, index):
        return self.regions[index]

    def __repr__(self):
        return str(self.regions)


class View:
    def __init__(self, text, region_set=None):
        self.region_set = region_set
        self.text = text

    def sel(self):
        return self.region_set

    def run_command(self, command, args):
        commands = {'expand_selection': self._expand_selection}
        commands[command](**args)

    def substr(self, region):
        # Test it
        return self.text[region.begin():region.end() + 1]

    def _expand_selection(self, to):
        if to == 'line':
            self.region_set[0].a = 0
            self.region_set[0].b = len(self.text) - 1
