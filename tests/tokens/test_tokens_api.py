from __future__ import unicode_literals

from spacy.tokens import Doc

import pytest


@pytest.mark.models
def test_getitem(EN):
    tokens = EN(u'Give it back! He pleaded.')
    assert tokens[0].orth_ == 'Give'
    assert tokens[-1].orth_ == '.'
    with pytest.raises(IndexError):
        tokens[len(tokens)]


@pytest.mark.models
def test_serialize(EN):
    tokens = EN(u'Give it back! He pleaded.')
    packed = tokens.to_bytes()
    new_tokens = Doc(EN.vocab).from_bytes(packed)
    assert tokens.string == new_tokens.string
    assert [t.orth_ for t in tokens] == [t.orth_ for t in new_tokens]
    assert [t.orth for t in tokens] == [t.orth for t in new_tokens]


@pytest.mark.models
def test_serialize_whitespace(EN):
    tokens = EN(u' Give it back! He pleaded. ')
    packed = tokens.to_bytes()
    new_tokens = Doc(EN.vocab).from_bytes(packed)
    assert tokens.string == new_tokens.string
    assert [t.orth_ for t in tokens] == [t.orth_ for t in new_tokens]
    assert [t.orth for t in tokens] == [t.orth for t in new_tokens]
