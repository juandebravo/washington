import unittest
import logging
import os

from pyshould import should

from StringIO import StringIO
from types import GeneratorType

from washington.main import coroutine


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

