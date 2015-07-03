import re
import os
from functools import partial

from .register import register

def coroutine(func):
    """
    Wrap a function that is created to be a coroutine to
    call automatically `.next()` method to ensure we're moving
    to the first `yield` expression.
    """
    def wrapper(*args, **kw):
        gen = func(*args, **kw)
        gen.next()
        return gen

    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__

    return wrapper


def pipeline(iterator):
    """
    Build an Execute instance that will encapsulate
    the steps sequence in the pipeline
    """

    class Execute(object):

        def __init__(self, iterator):
            self.stack = []  # List of functions to be executed
            self.iterator = iterator  # Elements to act in

        def __call__(self):
            """ Launch the coroutine pipeline """
            n = len(self.stack)
            # Complete every step in the pipeline with the
            # next coroutine to be executed
            for i, fn in enumerate(reversed(self.stack)):
                if i > 0:
                    self.stack[n-i-1] = fn(self.stack[n-i])
                else:
                    # Last coroutine should not have a destination
                    self.stack[n-i-1] = fn(None)

            for e in self.iterator:
                # Call the first coroutine and let the flow progress
                # throw the destinations chain
                self.stack[0].send(e)

            # Ensure we're free-ing the resources
            self.stack[0].close()

        def __getattr__(self, value):
            """
            Hack the method missing to enable a chainable API
            """
            def wrapper(*args):
                """
                Creates a partially applied function, just missing
                the last argument, which is the `destination` coroutine
                and will be added upon calling the Execute instance
                """
                fn = partial(fname, *args)
                self.stack.append(lambda x: fn(x))
                return self

            if value in register:
                fname = register[value]
            else:
                # Raise an exception if the function is undefined
                raise AttributeError("Invalid function %s" % value)

            return wrapper

    return Execute(iterator)


def direct_pipeline(employees, destination):
    def execute():
        for e in employees:
            destination.send(e)
        # Free resources
        destination.close()

    return execute


__all__ = ['coroutine', 'pipeline', 'direct_pipeline']
