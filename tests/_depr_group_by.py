from __future__ import unicode_literals

import pytest

from spacy import en
from spacy.lexeme import lex_of

from spacy import LEX, NORM, SHAPE, LAST3

def test_group_by_lex():
    tokens = en.tokenize("I like the red one and I like the blue one")
    names, hashes, groups = tokens.group_by(LEX)

    assert len(groups[0]) == 2
    assert en.unhash(lex_of(groups[0][0])) == 'I'
    assert names[0] == 'I'
    assert len(groups[1]) == 2
    assert en.unhash(lex_of(groups[1][0])) == 'like'
    assert names[1] == "like"
    assert len(groups[2]) == 2
    assert len(groups[3]) == 1


def test_group_by_last3():
    tokens = en.tokenize("I the blithe swarthy mate ate on the filthy deck")
    names, hashes, groups = tokens.group_by(LAST3)

    assert len(groups[0]) == 1
    assert en.unhash(lex_of(groups[0][0])) == 'I'
    assert len(groups[1]) == 3
    assert en.unhash(lex_of(groups[1][0])) == 'the'
    assert len(groups[2]) == 2
    assert len(groups[3]) == 2
    assert len(groups[4]) == 1
