from kwlist import KeywordList
import pytest


# # # # # # # # # # #
# # #  FIXTURES # # #
# # # # # # # # # # #

@pytest.fixture
def kw(request):
    try:
        base_data = request.function.initial
    except AttributeError:
        base_data = []
    inst = KeywordList(*base_data)
    yield inst
    # assert instance not mutated
    assert inst == base_data


def initial(state):
    def decorator(func):
        func.initial = state
        return func
    return decorator


# # # # # # # # # # #
# # # # TESTS # # # #
# # # # # # # # # # #


# # Constructor Tests # #

def test_init_from_k_v_tuples():
    vals = ('a', 1), ('b', 2)
    m = KeywordList(*vals)
    assert m._map == list(vals)


def test_init_from_kw_args():
    m = KeywordList(a=1, b=2)
    sorted_mapping = sorted(m._map, key=lambda t: t[0])
    assert sorted_mapping == [('a', 1), ('b', 2)]


def test_init_from_k_v_tuples_and_kw_args():
    vals = ('a', 1), ('b', 2)
    m = KeywordList(*vals, a=3, b=4)
    sorted_mapping = sorted(m._map, key=lambda t: t[0])
    assert sorted_mapping == [('a', 1), ('a', 3), ('b', 2), ('b', 4)]


def test_init_non_string_keyword():
    try:
        KeywordList((None, 1))
    except TypeError:
        pass
    else:
        assert False, "Expected TypeError to be raised"


# # Identity and Equality Tests # #

def test_a_bunch():
    l = KeywordList(('a', 2), ('b', 3), ('a', 4))

    assert l == l
    assert l != KeywordList(('a', 2), ('b', 3))
    assert l == [('a', 4), ('b', 3), ('a', 2)]


def test_identity(kw):
    assert kw is kw


def test_self_equality(kw):
    assert kw == kw


def test_other_equality(kw):
    other = KeywordList()
    assert other == kw


@initial([('a', 1)])
def test_tuple_list_equality(kw):
    assert kw == [('a', 1)]
    assert [('a', 1)] == kw


def test_tuple_list_equality_empty(kw):
    assert kw == []


def test_inequality_different_keys(kw):
    other = KeywordList(('a', 1))
    assert other != kw


def test_inequality_different_keys_list(kw):
    other = [('a', 1)]
    assert other != kw


@initial([('a', 1)])
def test_inequality_different_values_list(kw):
    other = [('a', 1), ('a', 1)]
    assert other != kw


@initial([('a', 1)])
def test_inequality_different_number_of_keys(kw):
    other = KeywordList(*[('a', 1), ('a', 1)])
    assert other != kw


@initial([('a', 1)])
def test_inequality_different_values(kw):
    other = KeywordList(('a', 2))
    assert other != kw


def test_inequality_unsupported_type(kw):
    assert kw != ()
    assert kw != {}
    assert kw != 0
    assert kw != ''
    assert kw != None  # noqa
    assert kw != False  # noqa
    assert kw != object()


@initial([
    ('a', 1), ('a', 1), ('a', 1),
    ('b', 1), ('b', 1), ('b', 1)
])
def test_inequality_multiple_entries(kw):
    other = KeywordList(
        ('a', 1), ('a', 1),
        ('b', 1), ('b', 1), ('b', 1), ('b', 1)
    )
    assert other != kw


# # Built-in Method Tests # #

def test_repr_empty(kw):
    assert repr(kw) == """KeywordList[]"""


@initial([('a', 1), ('b', 2)])
def test_repr_with_values(kw):
    assert repr(kw) == """KeywordList[a: 1, b: 2]"""


@initial([('a', 1), ('b', 2)])
def test_repr_truncated_items(kw):
    assert kw._val_repr(max_items=1) == """[a: 1, ...]"""


@initial([('a', 2)])
def test_getitem(kw):
    assert kw['a'] == 2


def test_getitem_missing_raises_key_error(kw):
    try:
        kw['a']
    except KeyError:
        pass
    else:
        assert False, "Expected KeyError to be raised"


def test_len_no_length(kw):
    assert len(kw) == 0


@initial([('a', n) for n in range(10)])
def test_len(kw):
    assert len(kw) == 10


def test_key_iteration_empty(kw):
    assert [i for i in kw] == []


@initial([('a', 1), ('b', 2), ('c', 3)])
def test_key_iteration(kw):
    assert [i for i in kw] == ['a', 'b', 'c']


@initial([('a', 1)])
def test_contains(kw):
    assert 'a' in kw


def test_contains_missing(kw):
    assert 'b' not in kw


@initial([('a', 1)])
def test_concat_keyword_lists(kw):
    m = kw + KeywordList(('b', 2))
    assert m == [('a', 1), ('b', 2)]


@initial([('a', 1)])
def test_concat_keyword_list_to_list(kw):
    m = kw + [('b', 2)]
    assert m == [('a', 1), ('b', 2)]


@initial([('a', 1)])
def test_concat_keyword_lists_prepend(kw):
    m = kw.prepend(KeywordList(('b', 2)))
    assert m == [('a', 1), ('b', 2)]
    assert list(m.keys()) == ['b', 'a']


@initial([('a', 1)])
def test_concat_keyword_list_to_list_prepend(kw):
    m = [('b', 2)] + kw
    assert m == [('a', 1), ('b', 2)]
    assert list(m.keys()) == ['b', 'a']


def test_concat_invalid_type(kw):
    try:
        kw + {}
    except TypeError:
        pass
    else:
        assert False, "Expected TypeError to be raised"


def test_concat_prepend_invalid_type(kw):
    try:
        {} + kw
    except TypeError:
        pass
    else:
        assert False, "Expected TypeError to be raised"


def test_multiply_empty(kw):
    assert kw * 2 == []


def test_multiply_commutative(kw):
    assert 2 * kw == []


@initial([('a', 1), ('b', 2)])
def test_multiply(kw):
    assert kw * 2 == [('a', 1), ('b', 2), ('a', 1), ('b', 2)]


# # Public Method Tests # #

@initial([('a', 1)])
def test_get(kw):
    assert kw.get('a') == 1


def test_get_missing(kw):
    assert kw.get('a') is None


def test_get_missing_specified_default(kw):
    sentinel = object()
    assert kw.get('a', sentinel) is sentinel


@initial([('a', 1), ('b', 2), ('c', 3)])
def test_keys_view(kw):
    key_iter = kw.keys()
    assert list(key_iter) == ['a', 'b', 'c']


@initial([('a', 1), ('b', 2), ('c', 3)])
def test_keys_iterator_membership(kw):
    key_iter = kw.keys()
    assert 'a' in key_iter


@initial([('a', 1), ('b', 2), ('c', 3)])
def test_values_view(kw):
    value_iter = kw.values()
    assert list(value_iter) == [1, 2, 3]


@initial([('a', 1), ('b', 2), ('c', 3)])
def test_values_view_membership(kw):
    value_iter = kw.values()
    assert 1 in value_iter


@initial([('a', 1), ('a', 2), ('b', 3)])
def test_get_all(kw):
    assert list(kw.get_all('a')) == [1, 2]


def test_get_all_missing(kw):
    assert list(kw.get_all('a')) == []


def test_put(kw):
    sentinel = object()
    m = kw.put('a', sentinel)
    assert m['a'] is sentinel


@initial([('a', 1)])
def test_put_existing_key(kw):
    m = kw.put('a', 2)
    assert m == [('a', 2)]


def test_put_new_no_existing_key(kw):
    m = kw.put_new('a', 2)
    assert m == [('a', 2)]


@initial([('a', 1), ('a', 2)])
def test_put_new_existing_key(kw):
    m = kw.put_new('a', 3)
    assert m == [('a', 1), ('a', 2)]


@initial([('a', 1)])
def test_delete(kw):
    m = kw.delete('a')
    assert m == []


@initial([('a', 1), ('a', 2)])
def test_delete_with_val(kw):
    m = kw.delete('a', 2)
    assert m == [('a', 1)]


@initial([('a', 1), ('a', 2), ('b', 3)])
def test_delete_all(kw):
    m = kw.delete('a')
    assert m == [('b', 3)]


@initial([('a', 1), ('a', 2)])
def test_delete_first(kw):
    m = kw.delete_first('a')
    assert m == [('a', 2)]


def test_delete_first_empty(kw):
    m = kw.delete_first('b')
    assert m == kw


@initial([('a', 1)])
def test_delete_first_none_found_non_empty(kw):
    m = kw.delete_first('b')
    assert m == kw


@initial([('a', 1)])
def test_update(kw):
    m = kw.update('a', lambda n: n + 1)
    assert m == [('a', 2)]


def test_update_missing_key(kw):
    try:
        kw.update('a', lambda n: None)
    except KeyError:
        pass
    else:
        assert False, "Expected KeyError to be raised"


def test_update_initial_value(kw):
    m = kw.update('a', lambda n: None, 123)
    assert m == [('a', 123)]


@initial([('a', 1), ('b', 2), ('a', 3)])
def test_update_many_entries(kw):
    m = kw.update('a', lambda n: n + 1)
    assert m == [('b', 2), ('a', 2)]


@initial([('a', 1)])
def test_drop_single_key(kw):
    m = kw.drop('a')
    assert m == []


@initial([('a', 1), ('b', 2), ('c', 3), ('a', 4), ('c', 5)])
def test_drop_multiple_keys(kw):
    keys = ['a', 'b']
    m = kw.drop(*keys)
    assert m == [('c', 3), ('c', 5)]


@initial([('a', 1)])
def test_drop_key_missing(kw):
    m = kw.drop('b')
    assert m == kw


def test_split_empty(kw):
    l, m = kw.split('a')
    assert l == []
    assert m == []


@initial([('a', 1), ('b', 2), ('c', 3)])
def test_split(kw):
    splits = ['a', 'c', 'e']
    l, m = kw.split(*splits)
    assert l == [('a', 1), ('c', 3)]
    assert m == [('b', 2)]


@initial([('a', 1), ('b', 2), ('c', 3), ('a', 4)])
def test_split_multiple_entries(kw):
    splits = ['a', 'c', 'e']
    l, m = kw.split(*splits)
    assert l == [('a', 1), ('c', 3), ('a', 4)]
    assert m == [('b', 2)]


@initial([('a', 1), ('b', 2), ('a', 3)])
def test_count(kw):
    assert kw.count('a') == 2
    assert kw.count('b') == 1
    assert kw.count('c') == 0


def test_transform_empty(kw):
    assert kw.transform(lambda v: v) == []


@initial([('a', 1), ('b', 2), ('a', 3)])
def test_transform_all(kw):
    assert kw.transform(lambda v: v * 2) == [('a', 2), ('b', 4), ('a', 6)]


@initial([('a', 1), ('b', 2), ('a', 3)])
def test_transform_some(kw):
    transformed = kw.transform(lambda v: v * 2, key_match=lambda k: k == 'a')
    assert transformed == [('a', 2), ('b', 2), ('a', 6)]
