from __future__ import unicode_literals

from spacy.tokens import Doc

import pytest


def test_getitem(EN):
    tokens = EN(u'Give it back! He pleaded.')
    assert tokens[0].orth_ == 'Give'
    assert tokens[-1].orth_ == '.'
    with pytest.raises(IndexError):
        tokens[len(tokens)]


def test_serialize(EN):
    tokens = EN(u' Give it back! He pleaded. ')
    packed = tokens.serialize()
    new_tokens = Doc.deserialize(EN.vocab, packed)
    assert tokens.string == new_tokens.string
    assert [t.orth_ for t in tokens] == [t.orth_ for t in new_tokens]
    assert [t.orth for t in tokens] == [t.orth for t in new_tokens]
