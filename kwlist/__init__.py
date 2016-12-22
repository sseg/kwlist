from collections import defaultdict, Counter
from itertools import tee, filterfalse, starmap
from sys import intern


SENTINEL = object()


class KeywordList:
    def __init__(self, *items, **kw_items):
        collected_items = items + tuple(kw_items.items())
        try:
            self._map = [(intern(i[0]), i[1]) for i in collected_items]
        except TypeError as err:
            raise TypeError("Only string keywords can be used") from err

    def __repr__(self):
        return "{cls}{val}".format(
            cls=self.__class__.__name__,
            val=self._val_repr()
        )

    def _val_repr(self, max_items=50):
        items = self._map[:max_items]
        item_strings = ("%s: %s" % (k, repr(v)) for k, v in items)
        map_string = ', '.join(item_strings)
        if len(self) > max_items:
            map_string = map_string + ", ..."
        return "[%s]" % map_string

    def __getitem__(self, key):
        for k, v in self._map:
            if k == key:
                return v
        raise KeyError

    def __iter__(self):
        yield from starmap(lambda k, v: k, self._map)

    def __len__(self):
        return len(self._map)

    def __add__(self, other):
        if isinstance(other, KeywordList):
            return self._add_kwlist(other)
        if isinstance(other, list):
            as_kwlist = KeywordList(*other)
            return self._add_kwlist(as_kwlist)
        raise TypeError(
            "Can only concatenate KeywordList or list (not \"{other_type}\") to KeywordList".format(
                other_type=type(other)
            )
        )

    append = __add__

    def __radd__(self, other):
        if isinstance(other, KeywordList):
            return other._add_kwlist(self)
        if isinstance(other, list):
            as_kwlist = KeywordList(*other)
            return as_kwlist._add_kwlist(self)
        raise TypeError(
            "Can only concatenate KeywordList or list (not \"{other_type}\") to KeywordList".format(
                other_type=type(other)
            )
        )

    prepend = __radd__

    def __mul__(self, n):
        """
        Equivalent to adding a KeywordList to itself n times
        """
        return KeywordList(*(self._map * n))

    __rmul__ = __mul__

    def _add_kwlist(self, other):
        combined_maps = self._map + other._map
        return KeywordList(*combined_maps)

    def __eq__(self, other):
        """
        Two keywords are considered to be equal if they contain the same keys and those
        keys contain the same values.

        Equal comparison can be made between two KeywordList objects or one KeywordList
        object and a list of key-value tuples.

        NOTE: Ordering is not considered when evaluating equality.
        """
        if isinstance(other, KeywordList):
            return self._equal_kwlist(other)
        if isinstance(other, list):
            return self._equal_list(other)
        return False

    def _equal_kwlist(self, other):
        if set(self.keys()) != set(other.keys()):
            return False
        for k in self:
            if Counter(self.get_all(k)) != Counter(other.get_all(k)):
                return False
        return True

    def _equal_list(self, other):
        other_value_map = defaultdict(list)
        for t in other:
            other_value_map[t[0]].append(t[1])
        if set(self.keys()) != set(other_value_map.keys()):
            return False
        for k in self:
            if Counter(self.get_all(k)) != Counter(other_value_map[k]):
                return False
        return True

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        return iter(self)

    def values(self):
        yield from starmap(lambda k, v: v, self._map)

    def get_all(self, key):
        """
        Gets all values for a specific key.
        """
        for k, v in self._map:
            if k == key:
                yield v

    def put(self, key, value):
        """
        Puts the given value under key.

        If a previous value is already stored, all entries are removed and the value is
        overridden.
        """
        without_key = filter(lambda t: t[0] != key, self._map)
        return KeywordList(*[*without_key, (key, value)])

    def put_new(self, key, value):
        """
        Puts the given value under key unless the entry key already exists.
        """
        if key in self:
            return KeywordList(*self._map)
        return KeywordList(*[*self._map, (key, value)])

    def delete(self, key, value=SENTINEL):
        """
        Deletes the entries in the keyword list for a specific key.

        If a value is provided then only the entries with that value are deleted.
        If the key does not exist, or if no entries with the value exists, returns
        the keyword list unchanged.

        Use `delete_first` to delete just the first entry in  case of duplicated keys.
        """
        if value is SENTINEL:
            return self._delete_all(key)
        return self._delete_all_with_value(key, value)

    def _delete_all(self, key):
        return KeywordList(*filter(
            lambda t: t[0] != key,
            self._map
        ))

    def _delete_all_with_value(self, key, value):
        return KeywordList(*filter(
            lambda t: not(t[0] == key and t[1] == value),
            self._map
        ))

    def delete_first(self, key):
        """
        Deletes the first entry in the keyword list for a specific key.

        If the key does not exist, returns the keyword list unchanged.
        """
        try:
            occurrence = list(self.keys()).index(key)
        except ValueError:
            # key not found, return unchanged
            return KeywordList(*self._map)

        without_occurrence = self._map[:occurrence] + self._map[occurrence + 1:]
        return KeywordList(*without_occurrence)

    def update(self, key, func, initial=SENTINEL):
        """
        Updates the key in keywords with the given function.

        If the key does not exist:
        - but an `initial` value is provided, then inserts the given value
        - if no `initial` value is provided then raises KeyError

        If there are duplicated keys, they are all removed and only the first one is
        updated.
        """
        if key not in self:
            if initial is SENTINEL:
                raise KeyError('Key "%s" not found' % key)
            return self.put_new(key, initial)
        return self.put(key, func(self[key]))

    def drop(self, *keys):
        """
        Drops the given keys from the keyword list.
        """
        without_keys = filter(lambda t: t[0] not in keys, self._map)
        return KeywordList(*without_keys)

    def split(self, *keys):
        """
        Takes all entries corresponding to the given keys and extracts them into a
        separate keyword list.

        Returns a tuple with the new list and the old list with removed keys.

        Keys for which there are no entires in the keyword list are ignored.

        Entries with duplicated keys end up in the same keyword list.
        """
        predicate = lambda e: e[0] in keys
        t1, t2 = tee(iter(self._map))
        m_true, m_false = filter(predicate, t1), filterfalse(predicate, t2)
        return KeywordList(*m_true), KeywordList(*m_false)

    def count(self, key):
        """
        Counts the total number of occurrences of key in the keyword list.
        """
        return len(list(filter(lambda t: t[0] == key, self._map)))

    def transform(self, func, key_match=None):
        """
        Applies a transform function to all values.

        If a key_match function is provided then only those elements whose key
        returns True will be transformed.
        """
        if key_match is None:
            key_match = lambda k: True
        return KeywordList(*(
            (k, func(v)) if key_match(k)
            else (k, v)
            for k, v in self._map
        ))
