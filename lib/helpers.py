"""Defines some useful python objects

author: Alexandr Skurihin [a.skurihin@gmail.com]
last-modified: 04.02.2012
"""


class AvailabilityChecker(object):
    """Makes 'in' checks easily.
    Apply given @comparators to checking object,
    if item in @comparators is not callable, checks if comparing object
    is equal to this item in @comparators


    >>>checker = AvailabilityChecker("checkme")
    >>>"checkme" in checker
    True
    >>>checker = AvailabilityChecker(lambda s: s.startswith('_'))
    >>>"_checkme" in checker
    True

    """
    def __init__(self, comparators):
        """
        @param {anytype} comparators
        """
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
        return any(cb(attr) for cb in self._comparators)


escape = lambda s: "\'" + s + "\'"

make_eq = lambda x: lambda y: x == y
