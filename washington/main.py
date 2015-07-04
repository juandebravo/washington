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


def pipeline(iterator, register=None):
    """
    Build an Execute instance that will encapsulate
    the steps sequence in the pipeline
    """
    register = register or globals()['register']

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
                try:
                    self.stack[0].send(e)
                except Exception as exc:
                    # https://github.com/mitsuhiko/jinja2/blob/master/jinja2/debug.py
                    #
                    # In case of an Exception is raised, it's exposed
                    # the entire coroutine chain till the point where
                    # the error occurred.
                    #
                    # Example:
                    #   Traceback (most recent call last):
                    #     File "examples.py", line 46, in <module>
                    #       filter_users_chain()
                    #     File "/Users/juan/projects/personal/washington/washington/main.py", line 53, in __call__
                    #       self.stack[0].send(e)
                    #     File "/Users/juan/projects/personal/washington/washington/library.py", line 14, in create_dict
                    #       destination.send(value)
                    #     File "/Users/juan/projects/personal/washington/washington/library.py", line 23, in filter_by
                    #       destination.send(x)
                    #     File "/Users/juan/projects/personal/washington/washington/library.py", line 42, in pluck
                    #       destination.send((yield)[field])
                    #   KeyError: 'alia'
                    #
                    # It might be good to change `destination.send by the real function name
                    #
                    # Example:
                    #   Traceback (most recent call last):
                    #     File "examples.py", line 46, in <module>
                    #       filter_users_chain()
                    #     File "/Users/juan/projects/personal/washington/washington/main.py", line 52, in __call__
                    #       create_dict()
                    #     File "/Users/juan/projects/personal/washington/washington/library.py", line 14, in create_dict
                    #       filter_by()
                    #     File "/Users/juan/projects/personal/washington/washington/library.py", line 23, in filter_by
                    #       pluck()
                    #     File "/Users/juan/projects/personal/washington/washington/library.py", line 42, in pluck
                    #       destination.send((yield)[field])
                    #   KeyError: 'alia'
                    # import sys
                    # exc_type, exc_value, exc_traceback = sys.exc_info()

                    # catch
                    # detect if next element in the stack is a catch clause
                    raise

                    #traceback.print_tb(exc_traceback, file=sys.stdout)
                    # print "*** print_exception:"
                    # traceback.print_exception(exc_type, exc_value, exc_traceback,
                    #                           limit=2, file=sys.stdout)
                    # print "*** print_exc:"
                    #traceback.print_exc()
                    # print "*** format_exc, first and last line:"
                    #formatted_lines = traceback.format_exc().splitlines()
                    #traceback.print_tb(exc_traceback)
                    #print exc_type.__name__ + ': ' + str(exc_value)
                    #print formatted_lines[-3]
                    #print '\n'.join([formatted_lines[0], formatted_lines[2], formatted_lines[-3], formatted_lines[-1]])
                    #print formatted_lines
                    #print "*** format_exception:"

                    #traceback = _make_traceback(exc_info, source_hint)
                    #exc_type, exc_value, tb = traceback.standard_exc_info
                    #reraise(exc_type, exc_value, tb)
                    # def fake_exc_info(exc, next_coroutine):
                    #     return exc

                    # frames = []
                    # tb = exc_traceback
                    # while tb is not None:
                    #     _next = tb.tb_next
                    #     tb = fake_exc_info((exc_type, exc_value) + (tb,), _next)[2]
                    #     frames.append(tb)
                    #     tb = _next

                    # traceback.print_tb(frames[0], file=sys.stdout)

                    # for (i, t) in enumerate(foo):
                    #     value = '  File "{0}", line {1}, in {2}'.format(t[0], t[1], t[2])
                    #     if len(values):
                    #         values[i-1] += '\n    {0}()'.format(t[2])
                    #     values.append(value)
                    # values[i]+= '\n    {0}'.format(foo[-1][3])

                    # print 'Traceback (most recent call last):'
                    # for v in values:
                    #     print v

                    # print '\n' + exc_type.__name__ + ': ' + str(exc_value)

                    # print repr(traceback.format_exception(exc_type, exc_value,
                    #                                        exc_traceback))
                    # print "*** extract_tb:"
                    # print repr(traceback.extract_tb(exc_traceback))
                    # print "*** format_tb:"
                    # print repr(traceback.format_tb(exc_traceback))
                    # print "*** tb_lineno:", exc_traceback.tb_lineno

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
                raise AttributeError("Invalid function %s not in %s" % (value, register))

            return wrapper

        def catch(self, fname):
            """
            Defines an exception handler to be executed when the previous
            coroutine raises an Exception
            """
            temp = self.stack[-1]
            _args = (fname,)
            self.stack[-1] = partial(register['tap'], *_args)
            self.stack.append(temp)
            return self



    return Execute(iterator)


def direct_pipeline(employees, destination):
    def execute():
        for e in employees:
            destination.send(e)
        # Free resources
        destination.close()

    return execute


__all__ = ['coroutine', 'pipeline', 'direct_pipeline']
