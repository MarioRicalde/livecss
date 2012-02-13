# -*- coding: utf-8 -*-
"""
    livecss.helpers
    ~~~~~~~~~

    This module implements some python helper objects.

    Usage examples:
    --------------
        >>> checker = AvailabilityChecker("checkme")
        >>> "checkme" in checker
        True
        >>> checker = AvailabilityChecker(lambda s: s.startswith('_'))
        >>> "_checkme" in checker
        True
        >>> checker = AvailabilityChecker((lambda s: s.startswith('_'), 4))
        >>> "__checkme" in checker
        True
        >>> 4 in checker
        True
        >>> 5 in checker
        False

"""


class AvailabilityChecker(object):
    """Provides convenient a in b checking.
    It works by applying given `comparators` to a comparing object.
    If item in `comparators` is not callable,
    checks if comparing object is equal to the item in `comparators`
    If `comparators` > 1, iterate over `comparators`, till first match.

    :param comparators: sequence of `comparators`,
                        where one `comparator` is expected to be a comparator function,
                        otherwise is turned into one, using :attr:`make_eq`

    """

    def __init__(self, comparators):
        if not isinstance(comparators, list) and \
           not isinstance(comparators, tuple):
            comparators = [comparators]

        self._comparators = []
        for cb in comparators:
            if not callable(cb):
                self._comparators.append(make_eq(cb))
            else:
                self._comparators.append(cb)

    def __contains__(self, attr):
        matches = []
        for cb in self._comparators:
            try:
                matches.append(cb(attr))
            except AttributeError:
                # if cb was applied to not supported type
                continue
        return any(matches)


escape = lambda s: "\'" + s + "\'"

make_eq = lambda x: lambda y: x == y
