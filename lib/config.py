from wrappers import PerFileConfig


class Config(PerFileConfig):
    def __init__(self, id):
        super(Config, self).__init__(id, 'per-file', in_memory=False)

    def __getattribute__(self, attr):
        if attr.startswith("global_"):
            rval = self._s[attr]
        else:
            rval = super(Config, self).__getattribute__(attr)
        return True if rval == None else rval

    def __setattr__(self, attr, value):
        if attr.startswith("global_"):
            self._s[attr] = value
        else:
            return super(Config, self).__setattr__(attr, value)


# class Config(PerFileConfig):
#     def __init__(self, id, colors=False):
#         super(Config, self).__init__(id=id,
#                                     settings_file='per-file',
#                                     in_memory=False,
#                                     ignored_props=lambda x: x.startswith('global_'))
#         self._colors = colors or []
#         self.global_on = True
