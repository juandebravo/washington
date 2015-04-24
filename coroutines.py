import re
from functools import partial


def coroutine(func):
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
            o_file.write(value + '\r\n')
            if destination is not None:
                destination.send(value)
    except GeneratorExit:
        o_file.close()


@coroutine
def pluck(field, destination):
    while True:
        destination.send((yield)[field])


def pipeline(employees):

    class Method(object):

        def __init__(self, method, execute):
            self.execute = execute
            self.fname = globals()[method]

        def __call__(self, *args):
            self.fn = partial(self.fname, *args)
            self.execute.stack.append(self)
            return self.execute

        def send(self, i):
            self.fn(self.execute.stack[i+1].fn)

    class Execute(object):

        def __init__(self, employees):
            self.stack = []
            self.employees = employees

        def __call__(self):
            for e in self.employees:
                self.stack[0].send(e)
            self.stack[0].close()

        def __getattr__(self, value):
            if value in ('create_dict', 'filter_by', 'pluck', 'print_name'):
                return Method(value, self)
            else:
                return self.__dict__.get(value)

    return Execute(employees)


employees = open('file.txt')

# alias_contains_u_not_at_the_beginning = pipeline(
#     employees,
#     create_dict(
#         ('alias', 'email', 'location'),
#         filter_by(
#             'alias',
#             r'^[^u]+u',
#             pluck(
#                 'alias',
#                 print_name('result.log')
#             )
#         )
#     )
# )

alias_contains_u_not_at_the_beginning = (pipeline(employees).
                                         create_dict(('alias', 'email', 'location')).
                                         filter_by('alias', r'^[^u]+u').
                                         pluck('alias').
                                         print_name('result.log'))

alias_contains_u_not_at_the_beginning()
