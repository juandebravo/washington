"""
Defines a generic container for registering chainable
coroutines to be used in the user program.
"""

class Registrar(object):

    def __init__(self):
        self._coroutines = {}

    def __call__(self, *fn):
        for f in fn:
            self._coroutines[f.__name__] = f

    def __iter__(self):
        for x in self._coroutines:
            yield x

    def __getitem__(self, value):
        return self._coroutines[value]


register = Registrar()

__all__ = ['register']
