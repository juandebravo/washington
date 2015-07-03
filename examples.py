import re
import os

from washington import direct_pipeline, pipeline
from washington.library import create_dict, filter_by, pluck, dumper, print_name

# Imperative way
for u in open('file.txt'):
    d = dict(zip(('alias', 'email', 'location'), u.split('|', 2)))
    patc = re.compile(r'^[^u]+u')
    if patc.search(d['alias']):
        os.sys.stdout.write(d['alias'])  # Python 2/3 compliance
        with open('result2.log', 'a') as f:
             f.write(d['alias'])


# Coroutines
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

# Coroutines using a chainable API
filter_users_chain = (pipeline(open('file.txt')).
                      create_dict(('alias', 'email', 'location')).
                      filter_by('alias', r'^[^u]+u').
                      pluck('alias').
                      dumper(os.sys.stdout.write).
                      print_name('result.log'))

filter_users_chain()
