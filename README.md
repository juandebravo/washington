# washington

Coroutines execution via a chainable API.

Washington is a simple library implemented with the only intention of having fun while learning about how to use coroutines in python.

Its main goal is to define a chainable API for *briding* a set of coroutines in a simple way.

## Example

Let's take the following example:

*Load a CSV file, create a dictionary in memory with its data, filter rows based on alias field, pluck the alias field and print the value to stdout and to a file.*

```python
# Imperative way
for u in open('file.txt'):
    d = dict(zip(('alias', 'email', 'location'), u.split('|', 2)))
    patc = re.compile(r'^[^u]+u')
    if patc.search(d['alias']):
        os.sys.stdout.write(d['alias'])  # Python 2/3 compliance
        with open('result2.log', 'a') as f:
             f.write(d['alias'])

# Washington
# Coroutines using a chainable API
filter_users_chain = (pipeline(open('file.txt')).
                      create_dict(('alias', 'email', 'location')).
                      filter_by('alias', r'^[^u]+u').
                      pluck('alias').
                      dumper(os.sys.stdout.write).
                      print_name('result.log'))

filter_users_chain()
```



# TODO
* [ ] How to address error handling? Following a promise-like API?
* [ ] Include a set of "common functions" to build a library working with coroutines? Such as `filter`, `pluck`. Partially done in washington/library.py
* [ ] How to include **sink** functions like `reduce` that should create a final result
