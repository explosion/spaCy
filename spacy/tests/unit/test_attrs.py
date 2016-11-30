from ...attrs import *


def test_key_no_value():
    int_attrs = intify_attrs({"ORTH": "dog"})
    assert int_attrs == {ORTH: "dog"}


def test_lower_key():
    int_attrs = intify_attrs({"norm": "dog"})
    assert int_attrs == {NORM: "dog"}



def test_lower_key_value():
    vals = {'dog': 10}
    int_attrs = intify_attrs({"lemma": "dog"}, strings_map=vals)
    assert int_attrs == {LEMMA: 10}


def test_idempotence():
    vals = {'dog': 10}
    int_attrs = intify_attrs({"lemma": "dog", 'is_alpha': True}, strings_map=vals)
    int_attrs = intify_attrs(int_attrs)
    assert int_attrs == {LEMMA: 10, IS_ALPHA: True}


def test_do_deprecated():
    vals = {'dog': 10}
    int_attrs = intify_attrs({"F": "dog", 'is_alpha': True}, strings_map=vals,
                             _do_deprecated=True)
    assert int_attrs == {ORTH: 10, IS_ALPHA: True}
