KeywordList
===========

kwlist provides a `KeywordList` class for associating string keywords with multiple values
in a consistent order.

This is useful for specifying multiple values for arguments as in HTTP headers or query parameters.

Inspired by Elixir's [Keyword](https://hexdocs.pm/elixir/Keyword.html) module.

Examples
--------

Basic usage:

```python
>>> from kwlist import KeywordList

>>> a = KeywordList(foo=1, bar=2)
>>> b = KeywordList(foo=3, baz=4)
>>> c = a + b
>>> c
KeywordList[foo: 1, bar: 2, foo: 3, baz: 4]
>>> a == [("foo", 1), ("bar", 2)]
True
>>> "bar" in b
False
>>> c["foo"]
1
>>> list(c.get_all("foo"))
[1, 3]
```

A `KeywordList` can be built by passing tuples of keyword-value pairs or keyword
arguments or both:

```python
>>> a = KeywordList(("foo", 1), ("bar", 2))
>>> b = KeywordList(foo=3, baz=4)
>>> a + b == KeywordList(("foo", 1), ("foo", 3), bar=2, baz=4)
True
```

Note that keyword argument ordering is only preserved in Python 3.6+ (see [PEP 468](https://www.python.org/dev/peps/pep-0468/)).

All methods of the `KeywordList` return new objects without mutating the object invoked:
```python
>>> original = KeywordList(a=2)
>>> original.update('a', lambda n: n + 1)
KeywordList[a: 3]
>>> original.delete('a')
KeywordList[]
>>> original.put('a', None)
KeywordList[a: None]
>>> original
KeywordList[a: 2]
```

This property simplifies arbitrary and complex operator chaining:
```python
>>> original = KeywordList()
>>> original.append([("foo", 1), ("foo", 2), ("bar", 3)]).transform(lambda x: str(x ** 2)).split("foo")
KeywordList[foo: '1', foo: '4'], KeywordList[bar: '9']
```

Installing
----------

Ideally in a [virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/), run:
```bash
git clone https://github.com/sseg/kwlist.git && pip install kwlist/
```

Similar Projects
----------------

If you're looking for something closer to Python's dict API you might like one of these implementations:
- [Werkzeug multidict](http://werkzeug.pocoo.org/docs/0.11/datastructures/#werkzeug.datastructures.MultiDict)
- [stdlib Headers object](https://docs.python.org/3/library/wsgiref.html?highlight=re#wsgiref.headers.Headers)
- [aiohttp multidict](https://github.com/aio-libs/multidict)
- [ordered multidict](https://github.com/gruns/orderedmultidict)


License
-------

BSD licensed. See the [LICENSE](https://github.com/sseg/kwlist/blob/master/LICENSE) file for details.
