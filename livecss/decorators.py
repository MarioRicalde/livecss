not_private = lambda s: not s.startswith("_")


def when(cb):

    def wrapper(kls):
        for method in filter(not_private, dir(kls)):
            print method
            original = getattr(kls, method)

            def __wrap(self, *args, **kwargs):
                if cb(*args):
                    print "Calling original"
                    return original(self, *args)
            setattr(kls, method, __wrap)

        return kls
    return wrapper


@when(lambda x: x == 'test')
class A(object):
    def test(self, test):
        return 42
