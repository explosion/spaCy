from __future__ import unicode_literals

import pytest

from spacy.en import English

NLU = English()


def test_merge_tokens():
    tokens = NLU(u'Los Angeles start.')
    assert len(tokens) == 4
    assert tokens[0].head.orth_ == 'Angeles'
    assert tokens[1].head.orth_ == 'start'
    tokens.merge(0, len('Los Angeles'), 'NNP', 'Los Angeles', 'GPE')
    assert len(tokens) == 3
    assert tokens[0].orth_ == 'Los Angeles'
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


def test_issue_54():
    text = u'Talks given by women had a slightly higher number of questions asked (3.2$\pm$0.2) than talks given by men (2.6$\pm$0.1).'
    tokens = NLU(text, merge_mwes=True)

