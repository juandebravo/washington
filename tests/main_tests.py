import unittest
import logging
from nose.plugins.skip import SkipTest

import os

from pyshould import should, all_of

from StringIO import StringIO
from types import GeneratorType

from washington import register
from washington.main import coroutine, pipeline


@coroutine
def uppercase(destination=None):
    while True:
        value = yield
        if destination is not None:
            destination.send(str(value).upper())


@coroutine
def collect(where, destination=None):
    while True:
        value = yield
        where.append(value)
        if destination is not None:
            destination.send(str(value).upper())

register(uppercase, collect)


class CorouteTestCase(unittest.TestCase):

    def setUp(self):
        self.stream = StringIO()
        self.handler = logging.StreamHandler(self.stream)
        self.log = logging.getLogger('')
        self.log.setLevel(logging.INFO)

        for handler in self.log.handlers:
            self.log.removeHandler(handler)

        self.log.addHandler(self.handler)

        @coroutine
        def add(start):
            """Sums two integers"""
            num = start
            self.log.info(start)
            while True:
                value = yield
                num = start + value
                self.log.info(num)

        self.fn = add

    def test_coroutine_returns_a_generator_type(self):
        start = 100
        t = self.fn(start)
        type(t) | should.eql(GeneratorType)

    def test_coroutine_keeps_function_doc(self):
        self.fn.__doc__ | should.eql("Sums two integers")

    def test_coroutine_keeps_function_name(self):
        self.fn.__name__ | should.eql("add")

    def test_coroutine_moves_to_first_yield_upon_initialized(self):
        start = 100
        t = self.fn(start)
        self.handler.flush()
        self.stream.getvalue() | should.eql(str(start) + os.linesep)


class PipelineTestCase(unittest.TestCase):

    def setUp(self):
        self.recollector = []
        self.pipeline = (
            pipeline((x for x in ('foo', 'bar', 'bazz')))
            .uppercase()
            .collect(self.recollector)
        )

    def test_chains_coroutines(self):
        self.pipeline()
        all_of(('FOO', 'BAR', 'BAZZ')) | should.be_in(self.recollector)
        len(self.recollector) | should.be(3)

    def test_raises_exception_if_invalid_coroutine(self):
        raise SkipTest

    def test_exposes_a_valid_stack_trace(self):
        raise SkipTest
