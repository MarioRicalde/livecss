escape = lambda s: "\'" + s + "\'"

make_eq = lambda x: lambda y: x == y


class AvailabilityChecker(object):
    def __init__(self, callbacks):
        if not isinstance(callbacks, list) and \
           not isinstance(callbacks, tuple):
            callbacks = [callbacks]

        self._callbacks = []
        for cb in callbacks:
            if not callable(cb):
                self._callbacks.append(make_eq(cb))
            else:
                self._callbacks.append(cb)

    def __contains__(self, attr):
        return any(cb(attr) for cb in self._callbacks)
