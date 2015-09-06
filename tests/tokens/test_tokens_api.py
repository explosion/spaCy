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


def test_set_ents(EN):
    tokens = EN.tokenizer(u'I use goggle chrone to surf the web')
    assert len(tokens.ents) == 0
    tokens.ents = [(EN.vocab.strings['PRODUCT'], 2, 4)]
    assert len(list(tokens.ents)) == 1
    assert [t.ent_iob for t in tokens] == [0, 0, 3, 1, 0, 0, 0, 0]
    ent = tokens.ents[0]
    assert ent.label_ == 'PRODUCT'
    assert ent.start == 2
    assert ent.end == 4
