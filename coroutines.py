import re


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


def pipeline(employees, destination):
    def execute():
        for e in employees:
            destination.send(e)
        destination.close()

    return execute


employees = open('file.txt')

alias_contains_u_not_at_the_beginning = pipeline(
    employees,
    create_dict(
        ('alias', 'email', 'location'),
        filter_by(
            'alias',
            r'^[^u]+u',
            pluck(
                'alias',
                print_name('result.log')
            )
        )
    )
)

alias_contains_u_not_at_the_beginning()
