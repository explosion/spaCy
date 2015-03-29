from __future__ import unicode_literals

import pytest

from spacy.en import English

NLU = English()


def test_merge_tokens():
    tokens = NLU(u'7 a.m. start.')
    assert len(tokens) == 4
    assert tokens[0].head.orth_ == 'a.m.'
    assert tokens[1].head.orth_ == 'start'
    tokens.merge(0, len('7 a.m.'), 'CD', '7 a.m.', 'TIME')
    assert len(tokens) == 3
    assert tokens[0].orth_ == '7 a.m.'
    assert tokens[0].head.orth_ == 'start'


def test_merge_heads():
    tokens = NLU(u'I found a pilates class near work.')
    assert len(tokens) == 8
    tokens.merge(tokens[3].idx, tokens[4].idx + len(tokens[4]), tokens[4].tag_,
                 'pilates class', 'O')
    assert len(tokens) == 7
    assert tokens[0].head.i == 1
    assert tokens[1].head.i == 1
    assert tokens[2].head.i == 3
    assert tokens[3].head.i == 1
    assert tokens[4].head.i in [1, 3]
    assert tokens[5].head.i == 4
