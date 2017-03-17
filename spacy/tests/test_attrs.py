# coding: utf-8
from __future__ import unicode_literals

from ..attrs import intify_attrs, ORTH, NORM, LEMMA, IS_ALPHA

import pytest


@pytest.mark.parametrize('text', ["dog"])
def test_attrs_key(text):
    assert intify_attrs({"ORTH": text}) == {ORTH: text}
    assert intify_attrs({"NORM": text}) == {NORM: text}
    assert intify_attrs({"lemma": text}, strings_map={text: 10}) == {LEMMA: 10}


@pytest.mark.parametrize('text', ["dog"])
def test_attrs_idempotence(text):
    int_attrs = intify_attrs({"lemma": text, 'is_alpha': True}, strings_map={text: 10})
    assert intify_attrs(int_attrs) == {LEMMA: 10, IS_ALPHA: True}


@pytest.mark.parametrize('text', ["dog"])
def test_attrs_do_deprecated(text):
    int_attrs = intify_attrs({"F": text, 'is_alpha': True},
                             strings_map={text: 10},
                             _do_deprecated=True)
    assert int_attrs == {ORTH: 10, IS_ALPHA: True}
