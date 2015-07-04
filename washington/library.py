import re
import os

from .main import coroutine
from .register import register


@coroutine
def tap(catch, destination):
    while True:
        u = yield
        try:
            destination.send(u)
        except Exception as ex:
            if not isinstance(ex, StopIteration):
                catch.send(u)


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

register(create_dict, filter_by, print_name, pluck, dumper, tap)
