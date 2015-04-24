import re
import os
from functools import partial


def coroutine(func):
    """
    Wraps a function that is created to be a coroutine to
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


@coroutine
def create_dict(keys, destination=None):
    while True:
        u = yield
        value = dict(zip(keys, u.split('|', 2)))
        if destination is not None:
            destination.send(value)


@coroutine
def filter_by(field, pattern, destination=None):
    while True:
        patc = re.compile(pattern)
        x = yield
        if patc.search(x[field]) and destination is not None:
            destination.send(x)


@coroutine
def print_name(fn, destination=None):
    o_file = open(fn, 'w')
    try:
        while True:
            value = yield
            o_file.write(value + os.linesep)
            if destination is not None:
                destination.send(value)
    except GeneratorExit:
        o_file.close()


@coroutine
def pluck(field, destination):
    while True:
        destination.send((yield)[field])


@coroutine
def dumper(out, destination):
    while True:
        value = yield
        out(value + os.linesep)
        destination.send(value)


def pipeline(iterator):
    """
    Function that creates and return an Execute instance that
    will encapsulate the different steps in the pipeline
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
                self.stack[0].send(e)

            self.stack[0].close()

        def __getattr__(self, value):
            """
            Hack the method missing to enable a chainable API
            """
            if value in globals():
                fname = globals()[value]

                def wrapper(*args):
                    """
                    Creates a partially applied function, just missing
                    the last argument, which is the `destination` coroutine
                    and will be added upon calling the Execute instance
                    """
                    fn = partial(fname, *args)
                    self.stack.append(lambda x: fn(x))
                    return self

                return wrapper
            else:
                # Raise an exception if the function is undefined
                raise AttributeError("Invalid function %s" % value)

    return Execute(iterator)


def direct_pipeline(employees, destination):
    def execute():
        for e in employees:
            destination.send(e)
        destination.close()

    return execute


filter_users_direct = direct_pipeline(
    open('file.txt'),
    create_dict(
        ('alias', 'email', 'location'),
        filter_by(
            'alias',
            r'^[^u]+u',
            pluck(
                'alias',
                dumper(
                    os.sys.stdout.write,
                    print_name('result.log')
                )
            )
        )
    )
)

filter_users_direct()

filter_users_chain = (pipeline(open('file.txt')).
                      create_dict(('alias', 'email', 'location')).
                      filter_by('alias', r'^[^u]+u').
                      pluck('alias').
                      dumper(os.sys.stdout.write).
                      print_name('result.log'))

filter_users_chain()
