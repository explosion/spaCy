# coding: utf-8
"""Test the possibly temporary workaround of flushing the stringstore of OOV words."""


from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize('text', [["a", "b", "c"]])
def test_stringstore_freeze_oov(stringstore, text):
    assert stringstore[text[0]] == 1
    assert stringstore[text[1]] == 2

    stringstore.set_frozen(True)
    s = stringstore[text[2]]
    assert s >= 4
    s_ = stringstore[s]
    assert s_ == text[2]

    stringstore.flush_oov()
    with pytest.raises(IndexError):
        s_ = stringstore[s]
